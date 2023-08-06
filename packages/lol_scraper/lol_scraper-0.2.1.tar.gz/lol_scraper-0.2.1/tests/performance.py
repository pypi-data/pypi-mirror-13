import logging
import os

# Load the dummy implementation of the network calls
os.environ['LOL_SCRAPER_TEST'] = "1"

from datetime import datetime as dt

from lol_scraper.match_downloader import download_matches, SINGLE_THREAD
from lol_scraper.initialize_configuration import prepare_config


conf = {
     "cassiopeia": {
        "api_key": "",
         "rate_limits": (3000, 10),
        "region": "KR"
    },
    "include_timeline": False,
    "seed_players_id" : [-10,-9,-8,-7,-6,-5,-4,-3,-2,-1]
}

class Container(): pass

def checkpoint(next_players, past_players, next_matches, past_matches):
    global ret
    ret = (next_players, past_players, next_matches, past_matches)

def check_perf(sleep_seconds=0, limits=((10,10),(500, 600))):
    def initialize(bucket_id, number_of_processes, conf):
        import tests.dummy
        tests.dummy.sleep_time = sleep_seconds

    store = Container()
    store.total_calls = 0
    store.start = None
    store.last = None
    store.partial_calls = 0
    store.avg = 0

    runtime_conf = prepare_config(conf)
    runtime_conf['cassiopeia']['rate_limits'] = limits

    def callback(match, tier, data, logger):
        now = dt.now()
        if store.start is None:
            store.start = now
        if store.last is None:
            store.last = now

        if store.total_calls % 10 == 0:
            elapsed_time = max(0.01, (now - store.last).total_seconds())
            total_time = max(0.01, (now - store.start).total_seconds())
            immediate = store.partial_calls / elapsed_time
            store.avg = (store.avg + immediate)/2
            logger.info("calls:%i  tot time:%i spd:%.2f avg spd:%.2f",
                        store.total_calls, total_time, store.total_calls/total_time, store.avg)
            store.last = now
            store.partial_calls = 0

        store.total_calls += 1
        store.partial_calls += 1

    logging.basicConfig(format='%(asctime)s, %(levelname)s, %(message)s',
                        datefmt="%m-%d %H:%M:%S",
                        level=logging.INFO)

    download_matches(runtime_conf, callback, checkpoint, parallelism=SINGLE_THREAD,
                     process_init_function=initialize)

if __name__ == '__main__':
    check_perf()