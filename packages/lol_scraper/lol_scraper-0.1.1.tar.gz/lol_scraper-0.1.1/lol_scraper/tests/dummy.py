import os
from lol_scraper.data_types import Tier
import random

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


match_file = os.path.join(os.path.dirname(__file__), 'match_string.json')
with open(match_file, 'rt') as f:
        match_string = f.read()
        from cassiopeia.type.dto.match import MatchDetail
        import json

import itertools
count = itertools.count(1)
sleep_time = 0.15
from collections import defaultdict
thread_id = itertools.count()
thread_names = defaultdict(lambda : next(thread_id))
exception_rate = 0#0.01

def get_match_list(*args, **kwargs):
    from cassiopeia.dto.requests import rate_limiter
    import time
    time.sleep(sleep_time)
    rate_limiter.call()
    obj = Bunch(matches=[Bunch(matchId=next(count))])
    if random.random() < exception_rate:
        raise ValueError()
    return obj

def get_match(*args, **kwargs):
    from cassiopeia.dto.requests import rate_limiter
    import time
    time.sleep(sleep_time)
    rate_limiter.call()

    match = MatchDetail(json.loads(match_string))
    match.matchId = next(count)
    if random.random() < exception_rate:
        raise ValueError()
    return match

def get_tier_from_participants(*args, **kwargs):
    from cassiopeia.dto.requests import rate_limiter
    import time
    rate_limiter.call()
    time.sleep(sleep_time)
    return Tier.challenger, {Tier.challenger: {next(count) for _ in range(10)}}