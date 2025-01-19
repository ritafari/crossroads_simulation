# Helper functions for message queue management

from queue import Queue

def create_queue():
    return Queue()

def enqueue(queue, item):
    queue.put(item)

def dequeue(queue):
    return queue.get() if not queue.empty() else None
