import os

from cassiopeia.baseriotapi import get_league_entries_by_summoner, get_summoners_by_name, get_versions
from cassiopeia.baseriotapi import get_challenger, get_master, get_match_list
from cassiopeia.baseriotapi import get_match_list, get_match
from cassiopeia.type.api.exception import APIError

if os.environ.get('LOL_SCRAPER_TEST', False):
    from tests.dummy import get_match, get_match_list