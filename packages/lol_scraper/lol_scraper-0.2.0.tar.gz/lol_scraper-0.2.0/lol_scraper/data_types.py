import threading
import datetime
import queue
import random
import logging
import sys
import time

import time as _time
from collections import deque
from enum import Enum, unique

from lol_scraper.concurrency.common import exc2pickle, task_done


@unique
class Queue(Enum):
    RANKED_SOLO_5x5 = 0
    RANKED_TEAM_3x3 = 1
    RANKED_TEAM_5x5 = 2


@unique
class Tier(Enum):
    challenger = 0
    master = 1
    diamond = 2
    platinum = 3
    gold = 4
    silver = 5
    bronze = 6

    @classmethod
    def equals_and_above(cls, tier):
        for t in cls:
            if t.is_better_or_equal(tier):
                yield t

    @classmethod
    def all_tiers_below(cls, tier):
        for t in cls:
            if not t.is_better_or_equal(tier):
                yield t

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        return hasattr(other, "value") and self.value == other.value

    def best(self, other):
        if self.value <= other.value:
            return self
        return other

    def worst(self, other):
        if self.value >= other.value:
            return self
        return other

    def is_better_or_equal(self, other):
        return self.value <= other.value

    @classmethod
    def parse(cls, tier):
        initial = tier[0].lower()
        if initial == 'b':
            return cls.bronze
        elif initial == 's':
            return cls.silver
        elif initial == 'g':
            return cls.gold
        elif initial == 'p':
            return cls.platinum
        elif initial == 'd':
            return cls.diamond
        elif initial == 'm':
            return cls.master
        elif initial == 'c':
            return cls.challenger
        else:
            raise ValueError("No Tier with name {}".format(tier))


@unique
class Maps(Enum):
    SUMMONERS_RIFT = 11


class SimpleCache():
    def __init__(self):
        self.store = {}

    def set(self, key, value, time=0):
        self.store[key] = (value, time, _time.time())

    def get(self, key, default=None):
        item = self.store.get(key, None)
        if item is None:
            return default
        else:
            value, time, put_time = item
            current_time = _time.time()
            # time = 0 means it never expires
            if put_time + time > current_time or time == 0:
                # it is still valid
                return value
            else:
                # expired value
                del self.store[key]
                return default


def cache_autostore(key, duration, cache, args_to_str=None, on_change=None):
    def make_key(*args, **kwargs):
        if args_to_str:
            return str(key) + args_to_str(*args, **kwargs)
        else:
            return key

    def function_decorator(wrapped):
        def wrapper(*args, **kwargs):
            sentinel = object()
            composed_key = make_key(*args, **kwargs)
            # get the value
            cached_value = cache.get(composed_key, sentinel)

            # if the value is saved or expired
            if cached_value is sentinel:
                # call the function which gives the real value
                new_value = wrapped(*args, **kwargs)
                # store it
                cache.set(composed_key, new_value, duration)
                # if we want to be notified of the change
                if on_change:
                    # get the old value
                    old = cache.get(composed_key + "_old")
                    # set the new value
                    cache.set(composed_key + "_old", new_value, 0)
                    if old != new_value:
                        on_change(old, new_value)
                # Then return the new value
                return new_value
            else:
                # The value stored was still fresh, return it
                return cached_value

        return wrapper

    return function_decorator


epoch = datetime.datetime.utcfromtimestamp(0)


def milliseconds_unix_time(dt=None):
    """
    Compute the milliseconds elapsed from the Unix Epoch (1/01/1970) to a specific date
    :param dt: A date. If it's equal to None, datetime.now() is used
    :return: The milliseconds since the Unix Epoch
    """
    if dt is None:
        dt = datetime.datetime.now()
    return int(unix_time(dt) * 1000)


def unix_time(dt):
    """
    Compute the seconds elapsed from the Unix Epoch (1/01/1970) to a specific date
    :param dt: A date
    :return: The seconds since the Unix Epoch
    """
    delta = dt - epoch
    return delta.total_seconds()


def do_every(seconds, func=None, *args, **kwargs):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + count * seconds - time.time(), 0)

    g = g_tick()
    while True:
        time.sleep(next(g))
        # This allows to use it in a for loop with a loop every 'seconds' seconds
        if func is None:
            yield
        else:
            func(*args, **kwargs)


class ConcurrentSet(set):
    """
    A set wrapped in a lock. THIS SET IS NOT SYNCHRONIZED AUTOMATICALLY, but makes it easier to use it as a synchronized
    set.
    To access it in a synchronized way use the context manager syntax:

    with this_set:
        this_set.add(item)
        this_set.pop()
        this_set.clear()

    """

    def __init__(self, seq=(), lock=None):
        super(ConcurrentSet, self).__init__(seq)
        if lock:
            if not hasattr(lock, '__enter__') and hasattr(lock, '__exit__'):
                raise ValueError("The lock must implement the context manager interface")
            self.lock = lock
        else:
            self.lock = threading.RLock()

    def __enter__(self):
        return self.lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.lock.__exit__(exc_type, exc_val, exc_tb)


class QueueMultiplexer:
    def __init__(self, bucket_id, local_queue, remote_queues, alpha=0.1):
        self.bucket_id = bucket_id
        self.local_q = local_queue
        self.remote_q = remote_queues
        self.num_partitions = len(remote_queues)
        self.weight = (1 + alpha )/ (self.num_partitions + alpha)

        assert bucket_id < self.num_partitions

        # When num_partition weight == 1. This prevents to get elements from the remote queue.
        # The behaviour is correct: since there is only one bucket the data will always be put in the local queue,
        # but the remote queue might contain some initial data when the multiplexer is created. We move them to the
        # local queue
        if self.num_partitions == 1:
            self._move_to_local_queue()

    def _move_to_local_queue(self):
        while True:
            try:
                self.local_q.put(self.remote_q[self.bucket_id].get(block=False))
                task_done(self.remote_q[self.bucket_id])
            except queue.Empty:
                break
            except queue.Full:
                break

    def get(self, block=True, timeout=None, weight=None):
        """
        Try getting an item from a queue. The queue is either the local queue or the remote queue with the id equal
        to this multiplexer bucket_id. The queue is chosen randomly, with weight defining the probability of picking
        the local queue.
        If the selected queue is empty, try to get(block=False) from the other queue (to not sleep more than
        the specified timeout)
        :param block:       See queue.Queue.get documentation
        :param timeout:     See queue.Queue.get documentation
        :param weight:      The probability to pick the local queue to perform the get operation.
                            Defaults to (1 + alpha) / (total_buckets + alpha)
        :return:            See queue.Queue.get documentation
        """
        if weight is None:
            weight = self.weight
        if random.random() < weight:
            first = self.local_q
            second = self.remote_q[self.bucket_id]
        else:
            second = self.local_q
            first = self.remote_q[self.bucket_id]

        try:
            item = first.get(block=False)
            task_done(first)
            return item
        except queue.Empty:
            item = second.get(block, timeout)
            task_done(second)
            return item

    def put(self, item, block=True, timeout=None):
        destination_bucket = item % self.num_partitions
        if destination_bucket == self.bucket_id:
            destination_queue = self.local_q
        else:
            destination_queue = self.remote_q[destination_bucket]

        destination_queue.put(item, block=block, timeout=timeout)

    def qsize(self, bucket=None):
        """
        Returns the sum of the elements in the local queue and in the queue specified by bucket
        :param bucket: The remote queue size to add to the local queue. Defaults to this multiplexer bucket_id
        :return: The size of the local queue plus the size of the remote queue at id equal to bucket
        """
        if bucket is None:
            bucket = self.bucket_id
        return self.local_q.qsize() + self.remote_q[bucket].qsize()


class FallbackQueue:
    def __init__(self, main_queue, fallback_queue):
        self.main_queue = main_queue
        self.fallback_queue = fallback_queue

    def get(self, block=True, timeout=None, **kwargs):
        # kwargs is used in order to provide the same interface as QueueMultiplexer
        try:
            item = self.main_queue.get(block=False)
            task_done(self.main_queue)
            return item
        except queue.Empty:
            item = self.fallback_queue.get(block=block, timeout=timeout)
            task_done(self.fallback_queue)
            return item

    def put(self, item, block=True, timeout=None):
        try:
            self.main_queue.put(item, block=False)
        except queue.Full:
            self.fallback_queue.put(item, block=block, timeout=timeout)

    def qsize(self, local_only=False):
        if local_only:
            return self.main_queue.qsize()
        else:
            return self.main_queue.qsize() + self.fallback_queue.qsize()

    def flush_to_fallback(self, block=True, timeout=None):
        """
        Moves all the items from the main queue to the fallback queue
        """
        while True:
            try:
                item = self.main_queue.get(block=False)
                task_done(self.main_queue)
                self.fallback_queue.put(item, block, timeout)
            except queue.Empty:
                return


class DistributedLogger():
    def __init__(self, level, queue, prologue=""):
        self._level = level
        self._queue = queue
        self._closed = False
        self._prologue = prologue

    @property
    def level(self):
        return self._level

    def getEffectiveLevel(self):
        return self._level

    def isEnabledFor(self, level):
        return level >= self._level

    def _log(self, level, message, *args, exc_info=None, exception=None, **kwargs):
        if self._closed:
            raise IOError("The logger is closed. You can't use it anymore")
        msg = self._prologue + (message % args)
        if exc_info:
            if exception:
                exc_info = (type(exception), exception, exception.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
            # else exc_info is a tuple and we use it as is
            self._queue.put((level, msg, exc2pickle(exc_info)))
        else:
            self._queue.put((level, msg))

    def log(self, level, msg, *args, **kwargs):
        if not isinstance(level, int):
            raise TypeError("level must be an integer")
        if self.isEnabledFor(level):
            self._log(level, msg, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.WARN):
            self._log(logging.WARN, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, message, *args, **kwargs)

    def exception(self, message="", *args, exc_info=True, **kwargs):
        kwargs['exc_info'] = exc_info
        self.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, message, *args, **kwargs)


class MessagePipe:
    def __init__(self, pipe):
        self.pipe = pipe

    def get(self, block=True, timeout=None):
        data_available = self.pipe.poll(timeout) if block else self.pipe.poll()
        if data_available:
            try:
                return self.pipe.recv()
            except EOFError:
                raise queue.Empty
        else:
            raise queue.Empty

    def put(self, item, block=True, timeout=None):
        try:
            self.pipe.send(item)
        except BrokenPipeError:
            raise queue.Full

    def get_ignore(self, ignore, block=True, timeout=None):
        while True:
            item = self.get(block, timeout)
            if ignore(item):
                continue
            return item


class Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
