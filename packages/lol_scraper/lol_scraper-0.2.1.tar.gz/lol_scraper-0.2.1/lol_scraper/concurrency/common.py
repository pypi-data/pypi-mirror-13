from tblib import pickling_support
import pickle

pickling_support.install()

def exc2pickle(exc_info):
    return pickle.dumps(exc_info)

def pickle2exc(pickled_exception):
    type, instance, traceback = pickle.loads(pickled_exception)
    return instance.with_traceback(traceback)

def task_done(queue):
    task_done = getattr(queue, 'task_done', None)
    task_done and task_done()

def close_queue(*queues):
    # Close the queues if they support it
    for queue in queues:
        if hasattr(queue, 'close'):
            queue.close()

    # Join the thread writing to the queue int he background if they have it
    for queue in queues:
        if hasattr(queue, 'join_thread'):
            queue.join_thread()