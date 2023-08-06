import pickle
import queue
import random
import threading

from lol_scraper.concurrency import worker
from lol_scraper.concurrency.common import close_queue
from lol_scraper.data_types import ConcurrentSet, QueueMultiplexer, DistributedLogger, FallbackQueue, Bunch
from lol_scraper.summoners_api import get_patch_changed, LATEST, consume_path_changed

MAX_LOCAL_QUEUE_SIZE = 50
EVICTION_SIZE = 50000
EVICTION_RATE = 0.2

# Token fields
TYPE = 0
PAYLOAD = 1

# Token recipients
MAIN_ID = -1
ANY = -2

# Token types
EXIT_REQUEST = 1
PAST_PLAYERS_AND_MATCHES = 2
INITIATING_SHUTDOWN = 3
SHUTDOWN_COMPLETED = 4
MONITORING_REQUEST = 5
MONITORING_RESPONSE = 6


def msg_ignore(*types):
    return lambda message: get_type(message) in types


def make_message(type, recipient, payload=None):
    return (type, payload)


def get_payload(message):
    return message[PAYLOAD]


def get_type(message):
    return message[TYPE]


# TODO change the queue.put() to use the timeout argument so that the process never blocks for too much


def _initialize_past_sets(bucket_id, main_connection, past_players, past_matches, logger):
    retries = 3
    while retries:
        try:
            _message = main_connection.get(timeout=1)
        except queue.Empty:
            retries -= 1
        else:
            if get_type(_message) == PAST_PLAYERS_AND_MATCHES:
                initial_past_players, initial_past_matches = get_payload(_message)
                past_players.update(initial_past_players)
                past_matches.update(initial_past_matches)
                return
    # retries got to 0. Notify that we didn't get the messages with the initial players
    logger.info("No player initialization messages where received in 3 tries. Continuing with empty set")


def _evict_players(past_players, logger):
    # past_players grows indefinitely. This doesn't make sense, as after a while a player have new
    # matches. When the list grows too big we remove part of the players, so that they can be analyzed again
    if len(past_players) > EVICTION_SIZE:
        total_players_pre_eviction = len(past_players)
        # Store the players to remove. We need to do this to be able to operate on the past_player object
        # directly, without changing it's reference, as the threads have an handle to the reference
        players_to_evict = {p_id for p_id in past_players if random.random() > EVICTION_RATE}
        past_players.difference_update(players_to_evict)
        msg = "Evicting analyzed players. Previously: {}. Now: {}".format(total_players_pre_eviction,
                                                                          len(past_players))
        logger.info(msg)


def _clear_past_matches(conf, past_matches, logger):
    # When a new patch is released, we can clear all the downloaded_matches if minimum_patch == 'latest'
    # Most of the time it will be False: do not acquire the lock in that case
    if get_patch_changed() and conf['minimum_patch'].lower() == LATEST:
        past_matches.clear()
        consume_path_changed()
        logger.info("New patch detected. Cleaned the downloaded matches set")


def download_and_execute(conf, bucket_id, mp_player_queues, mp_match_queues, mp_downloaded_matches, main_connection,
                         user_function, thread_init_function, logging_level, logging_queue,
                         initialization_function, number_of_threads):
    logger = DistributedLogger(logging_level, logging_queue, prologue="[Bucket {}] ".format(bucket_id))
    started_threads = []
    local_exit_request = Bunch(value=False)
    past_matches = None
    past_players = None
    next_player = None
    next_match = None
    downloaded_matches = None
    try:
        # The settings aren't transferred from one process to the other. Call an initialization function which should set
        # the state to what is needed for the execution
        init_func = pickle.loads(initialization_function)
        user_data = init_func(bucket_id, conf)

        # Initialize the queues to pass to the workers
        next_player = QueueMultiplexer(bucket_id, queue.Queue(maxsize=MAX_LOCAL_QUEUE_SIZE), mp_player_queues)
        next_match = QueueMultiplexer(bucket_id, queue.Queue(maxsize=MAX_LOCAL_QUEUE_SIZE), mp_match_queues)
        downloaded_matches = FallbackQueue(queue.Queue(maxsize=MAX_LOCAL_QUEUE_SIZE), mp_downloaded_matches)

        past_players = ConcurrentSet()
        past_matches = ConcurrentSet()
        # Initialize the past sets with the previous elements. Retry 5 times, after that continue, but notify the main
        _initialize_past_sets(bucket_id, main_connection, past_players, past_matches, logger)

        assert len(number_of_threads) == 3
        assert all(x >= 0 for x in number_of_threads)
        # TODO a smarter, automatic, dynamic evaluation of the number of threads to use is possible. Do it eventually
        num_player_threads, num_match_threads, num_user_threads = number_of_threads
        # Create and start the workers
        for i in range(num_player_threads):
            player_downloader = threading.Thread(name="PlayerDownloader%s" % i, target=worker.download_players, args=(
                conf, next_player, next_match, past_players, logger, local_exit_request))
            player_downloader.start()
            started_threads.append(player_downloader)
        logger.debug("Started Player Downloaders")

        for i in range(num_match_threads):
            match_downloader = threading.Thread(name="MatchDownloader%s" % i, target=worker.download_matches, args=(
                conf, next_match, next_player, downloaded_matches, past_matches, logger, local_exit_request))
            match_downloader.start()
            started_threads.append(match_downloader)
        logger.debug("Started Match Downloaders")

        user_func = pickle.loads(user_function)
        thread_init = pickle.loads(thread_init_function)
        for i in range(num_user_threads):
            user_func_executor = threading.Thread(name="UserFunctionExecutor%s" % i, target=worker.function_executor,
                                                  args=(user_func, downloaded_matches, thread_init, i, user_data,
                                                        logger, local_exit_request))
            user_func_executor.start()
            started_threads.append(user_func_executor)
        logger.debug("Started User Function Executor")

        # Monitor the execution
        while True:
            try:
                # Format: (type, payload)
                message = main_connection.get(timeout=10)
            except queue.Empty:
                pass
            else:
                if get_type(message) == EXIT_REQUEST:
                    logger.debug("Exit requested")
                    # Run the finally code and exit
                    return
                elif get_type(message) == MONITORING_REQUEST:
                    request_id = get_payload(message)
                    logger.debug("Received monitoring request %i", request_id)
                    payload = (
                        next_player.qsize(),
                        len(past_players),
                        next_match.qsize(),
                        len(past_matches),
                        downloaded_matches.qsize(local_only=True)
                    )
                    main_connection.put(make_message(MONITORING_RESPONSE, MAIN_ID, (request_id, payload)))
                    logger.debug("Sent monitoring response")
                else:
                    raise ValueError("Unexpected message: {}".format(message))

            _evict_players(past_players, logger)
            _clear_past_matches(conf, past_matches, logger)

    except:
        logger.exception("Exception in the controller of the process")
        raise
    finally:
        # We want to log the exceptions that might happen here
        try:
            logger.debug("Initiating shutdown")
            main_connection.put(make_message(INITIATING_SHUTDOWN, MAIN_ID))
            # TODO we might receive a EXIT_REQUEST if it was us who initiated the termination. Should we consume it?
            # Notify the threads to exit
            local_exit_request.value = True

            # Wait fot the threads to terminate
            for thread in started_threads:
                thread.join()
            logger.debug("Joined the threads")

            # Put in the multiprocess queues the data which was stored locally, so the main can inspect them
            main_connection.put(make_message(PAST_PLAYERS_AND_MATCHES, MAIN_ID,
                                             (past_players or set(), past_matches or set())))
            logger.debug("Sent the past player and matches")

            # Put the items in the local queues in the multiprocess queues. We need to be sure not to access the
            # multiplexer if it was not assigned before an exception brought us here
            # Bunch.get() will always raise a queue.Empty exception
            empty_queue = Bunch(get=lambda *args, **kwargs: (_ for _ in ()).throw(queue.Empty))
            for multiplexer, remote_queues in ((next_player or empty_queue, mp_player_queues),
                                               (next_match or empty_queue, mp_match_queues)):
                while True:
                    try:
                        player = multiplexer.get(block=False, weight=1)
                        remote_queues[bucket_id].put(player)
                    except queue.Empty:
                        break
            if downloaded_matches:
                downloaded_matches.flush_to_fallback()
            logger.debug("Flushed local queues to the multiprocess ones")

            # bucket 0 must not close the queues, as the main is still using them to join the other processes
            if bucket_id != 0:
                queues_to_close = mp_player_queues + mp_match_queues + [mp_downloaded_matches]
                close_queue(*queues_to_close)
                logger.debug("Closed the queues")
            main_connection.put(make_message(SHUTDOWN_COMPLETED, MAIN_ID, None))
        except:
            logger.exception("Exception while terminating the controller")
            raise
        else:
            logger.debug("Terminated successfully")
            logger.debug("Terminated successfully")