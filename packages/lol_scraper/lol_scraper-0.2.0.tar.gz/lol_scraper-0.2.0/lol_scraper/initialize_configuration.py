import datetime
import logging
import itertools
import urllib.error

from lol_scraper.cassiopeia_proxy import APIError, get_challenger, get_master, get_match_list

from lol_scraper.data_types import Tier, Queue, Maps, milliseconds_unix_time
from lol_scraper.summoners_api import summoner_names_to_id

delta_30_days = datetime.timedelta(days=30)

def prepare_config(config):
    runtime_config = {
        'cassiopeia': config['cassiopeia'],
        'logging_level': logging._nameToLevel[config.get('logging_level', 'NOTSET')],
        # Parse the time boundaries
        'end': None if 'end_time' not in config else datetime.datetime(**config['end_time']),
        'start': None if 'start_time' not in config else datetime.datetime(**config['start_time']),

        'minimum_patch': config.get('minimum_patch', ""),
        'queue': config.get('queue', Queue.RANKED_SOLO_5x5.name),
        'map_type': config.get('map', Maps.SUMMONERS_RIFT.name),
        'minimum_tier': config.get('minimum_tier', Tier.bronze.name).lower(),
        'include_timeline': config.get('include_timeline', True),

        'downloaded_matches': config.get('downloaded_matches', ()),
        'matches_to_download': config.get('matches_to_download', set()),
        'seed_players_id': config.get('seed_players_id', set())
    }

    if runtime_config['start'] is None:
        runtime_config['start'] = (runtime_config['end'] if runtime_config[
            'end'] else datetime.datetime.now()) - delta_30_days

    logger = logging.getLogger(__name__)
    if not runtime_config['seed_players_id']:
        # No players nor matches where provided, so we use the challenger and master players matches
        while True:
            try:
                config_seed_players = config.get('seed_players', None)
                if config_seed_players is None:
                    logger.info("No seed players detected. Downloading challenger and master players IDs.")
                    # Let's use challenger and master tier players as seed
                    runtime_config['seed_players_id'].update(int(league_entry_dto.playerOrTeamId) for league_entry_dto in
                                                        itertools.chain(get_challenger(runtime_config['queue']).entries,
                                                                        get_master(runtime_config['queue']).entries))
                else:
                    logger.info("Detected seed players names. Fetching the players IDs")
                    # We have a list of seed players. Let's use it
                    runtime_config['seed_players_id'].update(summoner_names_to_id(config_seed_players).values())

                break
            except APIError:
                # sometimes the network might have problems during the start. We don't want to crash just
                # because of that. Keep trying!
                logger.exception("APIError while initializing the script. Retrying")

    # We have the players ID, download the matches
    logger.info("Fetching up to 50 matches from the {} provided players".format(len(runtime_config['seed_players_id'])))
    while runtime_config['seed_players_id'] and len(runtime_config['matches_to_download']) < 50:
        player_id = runtime_config['seed_players_id'].pop()
        try:
            match_list = get_match_list(player_id, begin_time=milliseconds_unix_time(runtime_config['start']),
                            end_time=milliseconds_unix_time(runtime_config['end']),
                            ranked_queues=runtime_config['queue'])
            runtime_config['matches_to_download'].update(match.matchId for match in match_list.matches)
        except APIError:
            # Don't mind if some errors happen while downloading the matches
            continue
        except urllib.error.URLError:
            continue

    return runtime_config