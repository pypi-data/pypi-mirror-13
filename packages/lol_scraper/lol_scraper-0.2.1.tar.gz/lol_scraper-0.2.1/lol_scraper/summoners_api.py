import operator
import threading
from collections import defaultdict

from lol_scraper.data_types import Tier, Queue, SimpleCache, cache_autostore
from lol_scraper.cassiopeia_proxy import get_league_entries_by_summoner, get_summoners_by_name, get_versions

LATEST = "latest"
version_key = 'current_version'
_cache = SimpleCache()

_patch_changed_lock = threading.Lock()
_patch_changed = False


def _slice(start, stop, step):
    """
    Generate pairs so that you can slice from start to stop, step elements at a time
    :param start: The start of the generated series
    :param stop: The last of the generated series
    :param step: The difference between the first element of the returned pair and the second
    :return: A pair that you can use to slice
    """
    if step == 0:
        raise ValueError("slice() arg 3 must not be zero")
    if start == stop:
        raise StopIteration

    _previous = start
    _next = start + step
    while _next < stop:
        yield _previous, _next
        _previous += step
        _next += step
    yield _previous, stop


def leagues_by_summoner_ids(summoner_ids, queue=Queue.RANKED_SOLO_5x5):
    """
    Takes in a list of players ids and divide them by league tiers.
    :param summoner_ids: a list containing the ids of players
    :param queue: the queue to consider
    :return: a dictionary tier -> set of ids
    """
    summoners_league = defaultdict(set)
    for start, end in _slice(0, len(summoner_ids), 10):
        for player_id, leagues in get_league_entries_by_summoner(summoner_ids[start:end]).items():
            for league in leagues:
                if league.queue == queue.name:
                    summoners_league[Tier.parse(league.tier)].add(int(player_id))
    return summoners_league


def get_tier_from_participants(participants_identities, minimum_tier=Tier.bronze, queue=Queue.RANKED_SOLO_5x5):
    """
    Returns the tier of the lowest tier and the participantsIDs divided by tier
    player in the match
    :param participants_identities: the match participants
    :param minimum_tier: the minimum tier that a participant must be in order to be added
    :param queue: the queue over which the tier of the player is considered
    :return: the tier of the lowest tier player in the match
    """
    leagues = leagues_by_summoner_ids([p.player.summonerId for p in participants_identities], queue)
    match_tier = max(leagues.keys(), key=operator.attrgetter('value'))
    return match_tier, {league: ids for league, ids in leagues.items() if league.is_better_or_equal(minimum_tier)}


def summoner_names_to_id(summoners):
    """
    Gets a list of summoners names and return a dictionary mapping the player name to his/her summoner id
    :param summoners: a list of player names
    :return: a dictionary name -> id
    """
    ids = {}
    for start, end in _slice(0, len(summoners), 40):
        result = get_summoners_by_name(summoners[start:end])
        for name, summoner in result.items():
            ids[name] = summoner.id
    return ids


def set_patch_changed(*_, **__):
    with _patch_changed_lock:
        global _patch_changed
        _patch_changed = True


def consume_path_changed():
    with _patch_changed_lock:
        global _patch_changed
        _patch_changed = False


def get_patch_changed():
    with _patch_changed_lock:
        global _patch_changed
        return _patch_changed


@cache_autostore(version_key, 60 * 60, _cache, on_change=set_patch_changed)
def get_last_patch_version():
    version_extended = get_versions()[0]
    version = ".".join(version_extended.split(".")[:2])
    return version


def check_minimum_patch(patch, minimum):
    if not minimum:
        return True
    if minimum.lower() != LATEST:
        return patch >= minimum
    else:
        try:
            version = get_last_patch_version()
            return patch >= version
        except Exception:
            # in case the connection failed, do not store it, and try next round
            # Reject every version as we are not sure which is the latest version
            # and we don't want to pollute the data with patches with the wrong version
            return False
