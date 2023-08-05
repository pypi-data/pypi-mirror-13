import logging

from datetime import datetime as dt

import lol_scraper.tests.dummy
from lol_scraper.match_downloader import download_matches, prepare_config, setup_riot_api, Tier
from cassiopeia import baseriotapi


conf = {
     "cassiopeia": {
        "api_key": "a6c22e29-60b8-4775-81d5-26f5946c54fc",
        "region": "KR"
    },
    "include_timeline": False,
    "seed_players_id" : [-10,-9,-8,-7,-6,-5,-4,-3,-2,-1]
}

class Container(): pass

def check_performances(sleep_seconds=0, limits=((10,10),(500, 600)), total_count=1000):
    lol_scraper.tests.dummy.sleep_time = sleep_seconds
    baseriotapi.set_rate_limits(*limits)
    store = Container()
    store.calls = 0
    store.min = None
    store.max = dt.now()

    #setup_riot_api(conf)
    runtime_conf = prepare_config(conf)

    def callback(*args, **kwargs):
        now = dt.now()
        if store.calls > total_count:
            runtime_conf['exit'] = True
            return

        if store.min is None:
            store.min = now
        store.max= max(store.max, now)

        if store.calls % 10 == 0:
            print(store.calls, (store.max-store.min).seconds)

        store.calls += 1

    logging.basicConfig(format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
                        datefmt="%m-%d %H:%M:%S",
                        level=logging.INFO)

    download_matches(callback, None, runtime_conf)
    return store

if __name__ == '__main__':
    check_performances()