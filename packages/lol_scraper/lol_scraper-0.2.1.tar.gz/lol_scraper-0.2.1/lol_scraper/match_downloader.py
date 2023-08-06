import logging
import multiprocessing as mp
import os
import queue
import threading
import time


import cloudpickle
from cassiopeia import baseriotapi

from lol_scraper.concurrency import task, common, process_controller as ctrl
from lol_scraper.data_types import DistributedLogger, Bunch, MessagePipe

max_players_download_threads = int(os.environ.get('MAX_PLAYERS_DOWNLOAD_THREADS', 10))
matches_download_threads = int(os.environ.get('MATCHES_DOWNLOAD_THREADS', 10))
logging_interval = int(os.environ.get('LOGGING_INTERVAL', 60))

MAX_MULTIPROCESS_QUEUE_SIZE = 50

SINGLE_THREAD = 0
MULTI_THREAD = 1
#SINGLE_PROCESS = 2
MULTI_PROCESS = 3


def no_op(*args, **kwargs):
    pass


def setup_riot_api(cassiopeia_conf):
    baseriotapi.set_api_key(cassiopeia_conf['api_key'])
    baseriotapi.set_region(cassiopeia_conf['region'])

    limits = cassiopeia_conf.get('rate_limits', None)
    if limits is not None:
        if isinstance(limits[0], (list, tuple)):
            baseriotapi.set_rate_limits(*limits)
        else:
            baseriotapi.set_rate_limit(limits[0], limits[1])
    baseriotapi.print_calls(cassiopeia_conf.get('print_calls', False))


def _consume_elements(*operation_target_source):
    for operation, target, source in operation_target_source:
        while True:
            try:
                operation(target, source.get(block=False))
                common.task_done(source)
            except queue.Empty:
                break


def _remove_unprocessed_matches(target, item):
    match, tier = item
    target.remove(match.matchId)


def _prepare_initialization_function(conf, number_of_processes, user_initialization_function):
    cassiopeia_conf = {k: v for k, v in conf["cassiopeia"].items()}
    # No point in printing from other processes, as you can not read the stdout
    cassiopeia_conf.pop('print_calls', None)
    # Evenly divide the call limits between processes
    conf_limits = cassiopeia_conf.get('rate_limits', ((10, 10), (500, 600)))
    if isinstance(conf_limits[0], (list, tuple)):
        cassiopeia_conf['rate_limits'] = [(calls // number_of_processes, duration) for calls, duration in conf_limits]
    else:
        cassiopeia_conf['rate_limits'] = [(conf_limits[0] // number_of_processes, conf_limits[1])]

    def initialization_function(bucket_id, configuration):
        setup_riot_api(cassiopeia_conf)
        return user_initialization_function(bucket_id, number_of_processes, configuration)

    return initialization_function


def download_matches(conf, match_downloaded_callback, on_exit_callback=no_op, process_init_function=no_op,
                     thread_init_function=no_op, parallelism=SINGLE_THREAD, threads=None):
    """
    Fetches matches from the Riot API.
    It divides the matches and the players into buckets based on their ID and a partition function (the module operation
    over the ID). Every process handles one bucket, there are multiple threads per process to minimize the impact of
    latency over the download speed.
    A callback is executed every time a match is downlaoded


    :param conf:                        The configuration file specifying the fetching options

    :param match_downloaded_callback:   A function which is executed every time a match is downloaded. Takes as
                                        (the MatchDetail, the match tier, the thread data, the logger) as arguments.
                                        To see what the thread data is see thread_init_function

    :param on_exit_callback:            A function which is executed at the end of the collection process (after an exit
                                        request or in case of error).
                                        Takes (players yet to be analyzed, players already analyzed, matches yet to
                                        download, matches already downloaded). Defaults to no_op

    :param process_init_function:       A function which is executed in every process, before the worker threads are
                                        spawned. Takes (bucket_id, conf) as parameters, returns an object. Defaults to
                                        np_op

    :param thread_init_function:        A function which is executed in every thread, before the worker start it's
                                        operations. Takes (thread_index, user data), where user data is the object
                                        returned by process_init_function. Defaults to no_op

    :param parallelism:                 Specify the parallelism level of the user function. It can be SINGLE_THREAD,
                                        MULTI_THREAD or MULTI_PROCESS.
                                        SINGLE_THREAD:  execute the match_downloaded_callback in a thread in the main
                                                        process.

                                        MULTI_THREAD:   execute the match_download_callback in multiple threads in the
                                                        main process.

                                        MULTI_PROCESS:  execute the match_download_callback in multiple threads in all
                                                        the worker processes

    :param threads:                     A tuple (number of player download workers, number of match download workers,
                                        number of callback execution workers) specifying for each process how many
                                        threads should be spawned.
                                        NOTE: it's usually best to keep the match workers double of the player workers,
                                        as the match worker calls the Riot API 2 times for every match, while the
                                        player worker calls it once for every player.
    """

    NUMBER_OF_PROCESSES = int(os.environ.get('PROCESSES', 1))
    _underlying_logger = logging.getLogger("distributed_logger")
    # Defaults to SINGLE_THREAD, eg, 0 user function workers in the other processes
    if threads is None:
        threads = [1,2,0]
    else:
        threads = list(threads)

    if conf['logging_level'] != logging.NOTSET:
        logging_level = conf['logging_level']
        _underlying_logger.setLevel(logging_level)
    else:
        logging_level = _underlying_logger.getEffectiveLevel()

    def checkpoint(players_to_analyze, analyzed_players, matches_to_download, downloaded_matches):
        if on_exit_callback and on_exit_callback != no_op:
            try:
                on_exit_callback(players_to_analyze, analyzed_players, matches_to_download, downloaded_matches)
            except:
                _underlying_logger.exception("Exception while executing the checkpoint callback")
                raise
        _underlying_logger.info("Checkpoint callback executed successfully")

    next_players = set(conf['seed_players_id'])
    next_matches = set(conf['matches_to_download'])
    past_matches = set(conf['downloaded_matches'])
    past_players = set()

    if len(next_matches) == 0 and len(next_players) == 0:
        raise ValueError("You need to provide at least a match or a player to start fetching from")

    _underlying_logger.info("{} previously downloaded matches".format(len(past_matches)))
    _underlying_logger.info("{} matches to download".format(len(next_matches)))

    assert NUMBER_OF_PROCESSES > 0
    logger_thread = None
    logger_exit_request = Bunch(value=False)
    queue_type = mp.Queue if NUMBER_OF_PROCESSES > 1 else queue.Queue

    # The logger should never discard messages, so the queue is unbounded
    logging_queue = queue_type()

    # For the local worker use a thread queue, not a multiprocess one
    worker_connections, remote_connections = [], []
    for _ in range(NUMBER_OF_PROCESSES):
        conn1, conn2 = mp.Pipe()
        worker_connections.append(MessagePipe(conn1))
        remote_connections.append(MessagePipe(conn2))

    player_queues = [queue_type(maxsize=MAX_MULTIPROCESS_QUEUE_SIZE) for _ in range(NUMBER_OF_PROCESSES)]
    match_queues = [queue_type(maxsize=MAX_MULTIPROCESS_QUEUE_SIZE) for _ in range(NUMBER_OF_PROCESSES)]

    downloaded_matches = queue_type(maxsize=MAX_MULTIPROCESS_QUEUE_SIZE)
    local_bucket_id = 0

    processes = []
    logger = DistributedLogger(logging_level, logging_queue)
    try:
        logger_thread = threading.Thread(name="Logger",
                                         target=task.log_messages, args=(_underlying_logger, logging_queue, logger_exit_request))
        logger_thread.start()

        # Initialize the queues with the players and matches to download
        for player_id in next_players:
            _bucket_id = player_id % NUMBER_OF_PROCESSES
            try:
                player_queues[_bucket_id].put(player_id, block=False)
            except queue.Full:
                logger.warn("Ignoring some initial players (queue full)")
                break

        for match_id in next_matches:
            _bucket_id = match_id % NUMBER_OF_PROCESSES
            try:
                match_queues[_bucket_id].put(match_id, block=False)
            except queue.Full:
                logger.warn("Ignoring some initial matches (queue full)")
                break

        for _bucket_id, connection in enumerate(worker_connections):
            connection.put(ctrl.make_message(ctrl.PAST_PLAYERS_AND_MATCHES, _bucket_id,
                                             (past_players, past_matches)))

        # Since the execution must be single threaded, in the main process, the other processes should have0 0 user
        # function threads
        if parallelism in (SINGLE_THREAD, MULTI_THREAD):
            threads[2] = 0
        pickled_process_init = cloudpickle.dumps(_prepare_initialization_function(conf, NUMBER_OF_PROCESSES,
                                                                                  process_init_function))
        pickled_thread_init = cloudpickle.dumps(thread_init_function)
        pickled_user_function = cloudpickle.dumps(match_downloaded_callback)
        _bucket_id = 1
        for connection in remote_connections[1:]:
            p = mp.Process(name="ProcessBucket%s" % _bucket_id, target=ctrl.download_and_execute,
                           args=(conf, _bucket_id, player_queues, match_queues, downloaded_matches,
                                 connection, pickled_user_function, pickled_thread_init, logging_level,
                                 logging_queue, pickled_process_init, threads))
            processes.append(p)
            p.start()
            _bucket_id += 1

        # If the execution should be single threaded, we want 1 thread in the main process. If it's multi-threaded
        # we want the user to pick the number of user processes, but there should always be at least 1
        if threads[2] == 0  and parallelism in (MULTI_THREAD, MULTI_PROCESS):
            logger.warn("Execution set as MULTI_PROCESS or MULTI_THREAD, but 0 user threads per process were set. "
                        "Falling back to SINGLE_THREAD")
        threads[2] = max(1, threads[2])
        # Start a worker in this process as well
        local_worker = threading.Thread(name="ThreadBucket0", target=ctrl.download_and_execute,
                                        args=(conf, local_bucket_id, player_queues, match_queues, downloaded_matches,
                                              remote_connections[local_bucket_id], pickled_user_function,
                                              pickled_thread_init, logging_level, logging_queue,
                                              pickled_process_init, threads))
        processes.append(local_worker)
        local_worker.start()

        logger.info("Starting fetching..")

        # Send an ID when you make requests, so that you know to which request the response is
        monitoring_request_id = 0
        i = 0
        while not conf.get('exit', False):
            # Execute every LOGGING_INTERVAL seconds
            if i % logging_interval == 0:
                for _bucket_id, connection in enumerate(worker_connections):
                    connection.put(ctrl.make_message(ctrl.MONITORING_REQUEST, _bucket_id, monitoring_request_id))

                waiting_players = 0
                completed_players = 0
                waiting_matches = 0
                completed_matches = 0
                matches_to_process = 0

                # Here we send to the bucket a request to communicate us several statistics over their performances
                # We try 3 times to get the data from them, then we write the message ignoring the missing buckets
                not_replying_buckets = {x for x in range(len(worker_connections))}
                _retries = 3
                while not_replying_buckets and _retries:
                    _retries -= 1
                    for index, connection in enumerate(worker_connections):
                        if index in not_replying_buckets:
                            # We are still waiting for a response
                            try:
                                message = connection.get(timeout=0.5)
                            except queue.Empty:
                                pass
                            else:
                                type = ctrl.get_type(message)
                                if type == ctrl.MONITORING_RESPONSE:
                                    monitoring_response_id, payload = ctrl.get_payload(message)

                                    if monitoring_response_id != monitoring_request_id:
                                        logger.debug("Received a response id:%i instead of %i from bucket %i",
                                                     monitoring_response_id, monitoring_request_id, index)
                                        # Skip the old message
                                        continue

                                    w_players, c_players, w_matches, c_matches, l_process = payload
                                    waiting_players += w_players
                                    completed_players += c_players
                                    waiting_matches += w_matches
                                    completed_matches += c_matches
                                    matches_to_process += l_process
                                    not_replying_buckets.remove(index)
                                elif type == ctrl.INITIATING_SHUTDOWN:
                                    logger.info("Bucket %s terminated unexpectedly", index)
                                    return
                                else:
                                    raise ValueError("Unknown message: {}".format(message))

                _msg = ("Players in queue: %s. Players downloaded: %s. Matches in queue: %s. Matches downloaded: %s. "
                        "Matches waiting to be processed: %s")
                _log_args = [waiting_players, completed_players, waiting_matches, completed_matches,
                             matches_to_process + downloaded_matches.qsize()]

                # If not all buckets reported, add it to the message
                if not_replying_buckets:
                    _msg += ". Bucked which did not report: %s"
                    _log_args.append(", ".join(map(str, not_replying_buckets)))

                logger.info(_msg, *_log_args)

            i += 1
            time.sleep(1)

        logger.info("Terminating fetching")

    except KeyboardInterrupt:
        logger.info("user requested for exit")
        return
    except:
        _underlying_logger.exception("Exception in the main")
        raise
    finally:
        conf['exit'] = True
        logger.info("Initiating termination")
        logger.info("Sending the exit signal to the workers")
        for _bucket_id, connection in enumerate(worker_connections):
            try:
                connection.put(ctrl.make_message(ctrl.EXIT_REQUEST, _bucket_id))
            except queue.Full:
                # In the current implementation, connection is actually a Pipe connection. When the other process
                # terminates it closes the pipe. Sending an EXIT_REQUEST to a terminated process will thus result in a
                # BrokenPipeError, which gets wrapped as a queue.Full by the adapter (yeah, maybe not the best choice).
                # The process, if it terminated cleanly (it was not killed) will send all the information to the pipe
                # before exiting, so we already have the information we need. Just skip this error
                logger.debug("Bucket %s already terminated. Failed to send EXIT_REQUEST", _bucket_id)

        logger.info("Retrieving the data from the workers")
        past_players = set()
        past_matches = set()
        # Retrieve all the players who have been downloaded by the workers
        for connection in worker_connections:
            while True:
                # TODO: what if one process failed (and will never send a message)? Implement a retry mechanic
                message = connection.get_ignore(ctrl.msg_ignore(ctrl.INITIATING_SHUTDOWN, ctrl.MONITORING_RESPONSE))
                type = ctrl.get_type(message)
                if type == ctrl.PAST_PLAYERS_AND_MATCHES:
                    remote_past_players, remote_past_matches = ctrl.get_payload(message)
                    past_players.update(remote_past_players)
                    past_matches.update(remote_past_matches)
                    break
                else:
                    raise ValueError("Unexpected message: {}".format(message))

        logger.info("Consuming the queues and joining the workers")
        # We need to clear the queue where the process is writing in order to allow it to terminate
        next_players = set()
        next_matches = set()
        # Wait for all the processes to exit, consuming elements from the queue where they write to
        reported = []
        while len(reported) != len(worker_connections):
            for ind, (connection, player_q, match_q) in enumerate(zip(worker_connections, player_queues, match_queues)):
                # Skip the worker which already replied
                if ind in reported:
                    continue
                # Consume all the available items in the queue, so that the process has space to write them
                _consume_elements((set.add, next_players, player_q),
                                  (set.add, next_matches, match_q),
                                  (_remove_unprocessed_matches, past_matches, downloaded_matches))
                logger.debug("Consumed the queues for bucket %s", ind)
                # Check if the process has terminated
                try:
                    message = connection.get_ignore(ctrl.msg_ignore(ctrl.INITIATING_SHUTDOWN, ctrl.MONITORING_RESPONSE),
                                                    timeout=0.5)
                except queue.Empty:
                    pass
                else:
                    type = ctrl.get_type(message)
                    if type == ctrl.SHUTDOWN_COMPLETED:
                        reported.append(ind)
                        logger.debug("Bucket %s joined", ind)
                    else:
                        raise ValueError("Unexpected message: {}".format(message))

        # After all the processes terminated, clean a last time the queues
        for player_q, match_q in zip(player_queues, match_queues):
            _consume_elements((set.add, next_players, player_q),
                              (set.add, next_matches, match_q),
                              (_remove_unprocessed_matches, past_matches, downloaded_matches))

        # We don't need the queues anymore. Only leave the logger queue open
        # The queues must be empty
        queues_to_close = match_queues + player_queues + [downloaded_matches]
        assert all(not q.qsize() for q in queues_to_close), str([q.qsize() for q in queues_to_close])

        logger.info("Closing the queues")
        common.close_queue(*queues_to_close)

        logger.info("Joining the workers")

        # Joining workers once the queues are empty
        for worker in processes:
            worker.join()

        # At this point all workers terminate and it's not possible for them to generate new messages.
        # Terminate the logger
        logger.info("Terminating the distributed log writer")
        logger_exit_request.value = True
        logger_thread.join()

        # Always call the checkpoint, so that we can resume the download in case of exceptions.
        _underlying_logger.info("Calling checkpoint callback")
        checkpoint(next_players, past_players, next_matches, past_matches)
        _underlying_logger.info("Bye bye")
