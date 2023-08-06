import queue
import logging

from urllib.error import URLError
from lol_scraper.cassiopeia_proxy import APIError

from lol_scraper.concurrency.common import close_queue, pickle2exc

def _handle_exception(e, logger):
    if isinstance(e, APIError):
        if 400 <= e.error_code < 500:
            # Might be a connection problem
            logger.warning("Encountered error {}".format(e))
        elif 500 <= e.error_code < 600:
            # Server problem.
            logger.warning("Encountered error {}".format(e))
        else:
            logger.error("Encountered error {}".format(e))
    elif isinstance(e, URLError):
        logger.error("Encountered error {}. You are having connection issues".format(e))
    else:
        exc_info = (type(e), e, e.__traceback__)
        logger.error("Encountered unexpected exception {}".format(e), exc_info=exc_info)


def log_messages(logger, message_queue, exit_request):
    """
    :param logging.Logger           logger:
    :param queue.Queue              message_queue:
    :param multiprocessing.Value    exit_request:
    :return:
    """
    task_done = getattr(message_queue, 'task_done', lambda: None)
    while True:
        try:
            try:
                message = message_queue.get(timeout=0.5)
            except queue.Empty:
                # Only check for exit if there are no messages
                if exit_request.value:
                    break
                else:
                    continue
            else:
                task_done()

            level = message[0]
            msg = message[1]
            if len(message) == 2:
                logger.log(level, msg)
            elif len(message) == 3:
                exception = pickle2exc(message[2])
                _handle_exception(exception, logger)
        except Exception as e:
            _handle_exception(e, logger)
    close_queue(message_queue)