import queue
import os

if os.environ.get('LOL_SCRAPER_TEST', False):
    from tests.dummy import get_tier_from_participants
else:
    from lol_scraper.summoners_api import get_tier_from_participants

from lol_scraper.data_types import Maps, Tier, Queue, milliseconds_unix_time
from lol_scraper.summoners_api import check_minimum_patch
from lol_scraper.cassiopeia_proxy import get_match, get_match_list


class FetchingException(Exception):
    def __init__(self, match, msg):
        self.match = match
        self.short_message = msg

    def __repr__(self):
        return "Exception while fetching match {} due to '{}'".format(self.match, self.short_message)

    def __str__(self):
        return self.__repr__()


def fetch(fetch_function, send_result, conf, source, destination, previous, logger, exit_request):
    """

    :param dict                     conf:
    :param queue.Queue              source:
    :param Any                      destination:
    :param ConcurrentSet            previous
    :param DistributedLogger        logger:
    :param multiprocessing.Value    exit_request:
    :return:
    """
    while not exit_request.value:
        try:
            # Poll with a timeout so we can check for the exit condition
            try:
                # Task done is called by the QueueMultiplexer if it's needed
                item_id = source.get(timeout=1)
            except queue.Empty:
                continue

            with previous:
                if item_id in previous:
                    # Item already analyzed
                    continue
                else:
                    # Put it now, so other workers know they shouldn't download it
                    previous.add(item_id)

            try:
                value = fetch_function(item_id, conf)
            except:
                logger.exception()
                continue

            send_result(value, destination)
        except:
            logger.exception()


def _fetch_match(match_id, conf):
    try:
        match = get_match(match_id, conf['include_timeline'])
        if match.mapId == Maps[conf['map_type']].value:
            match_min_tier, participant_tiers = get_tier_from_participants(match.participantIdentities,
                                                                           Tier.parse(conf['minimum_tier']),
                                                                           Queue[conf['queue']])

            valid = (match_min_tier.is_better_or_equal(Tier.parse(conf['minimum_tier'])) and
                     check_minimum_patch(match.matchVersion, conf['minimum_patch']))
            return match, match_min_tier if valid else None, participant_tiers
        else:
            return None, None, {}
    except Exception as e:
        raise FetchingException(match_id, str(e)) from e


def _send_match_results(match_info, destination):
    match, tier, participant_tiers = match_info
    players_to_analyze, downloaded_matches = destination

    for player_id_set in participant_tiers.values():
        for player_id in player_id_set:
            try:
                # We don't care if the queue is full, that means we have enough players to analyze.
                players_to_analyze.put(player_id, block=False)
            except queue.Full:
                # Discard the player and all the subsequent ones
                break

    if tier:
        try:
            # The point of downloading matches is to analyze them. If the queue is full, sleep for a long time (5s) as
            # additional matches are not needed
            downloaded_matches.put((match, tier), timeout=1)
        except queue.Full:
            # Discard the match
            pass


def download_matches(conf, matches_to_download, players_to_analyze, downloaded_matches, past_matches, logger,
                     exit_request):
    """

    :param dict                     conf:
    :param queue.Queue              matches_to_download:
    :param queue.Queue              players_to_analyze:
    :param queue.Queue              downloaded_matches:
    :param ConcurrentSet            past_matches:
    :param DistributedLogger        logger:
    :param multiprocessing.Value    exit_request:
    :return:
    """
    try:
        return fetch(_fetch_match, _send_match_results, conf, matches_to_download,
                     (players_to_analyze, downloaded_matches),
                     past_matches, logger, exit_request)
    finally:
        logger.debug("Match download worker terminating")


def _fetch_player(player_id, configuration):
    match_list = get_match_list(player_id, begin_time=milliseconds_unix_time(configuration['start']),
                                end_time=milliseconds_unix_time(configuration['end']),
                                ranked_queues=configuration['queue'])
    return (match.matchId for match in match_list.matches)


def _send_player_results(match_list, matches_to_download):
    for match_id in match_list:
        try:
            # The only point of downloading players is to provide matches to download. If the queue is already full.
            # sleep for a long time (5s) as the data is not needed, we already have enough to process
            matches_to_download.put(match_id, timeout=1)
        except queue.Full:
            # Discard the processed element and all the subsequent ones
            break


def download_players(conf, players_to_analyze, matches_to_download, past_players, logger, exit_request):
    """

    :param dict                     conf:
    :param queue.Queue              players_to_analyze:
    :param queue.Queue              matches_to_download:
    :param ConcurrentSet            past_players
    :param DistributedLogger        logger:
    :param multiprocessing.Value    exit_request:
    :return:
    """
    try:
        return fetch(_fetch_player, _send_player_results, conf, players_to_analyze, matches_to_download, past_players,
                     logger, exit_request)
    finally:
        logger.debug("Player download worker terminating")


def function_executor(function, match_queue, thread_init_function, thread_index, user_data, logger, exit_request):
    try:
        thread_data = thread_init_function(thread_index, user_data)
    except Exception as e:
        logger.exception()
        raise

    while not exit_request.value:
        try:
            # task_done is called by the FallbackQueue
            match, tier = match_queue.get(timeout=1)
        except queue.Empty:
            continue
        try:
            function(match, tier, thread_data, logger)
        except Exception as e:
            logger.exception()

    logger.debug("User function worker terminating")
