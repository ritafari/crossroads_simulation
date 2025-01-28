# Helper functions for message queue management

from multiprocessing import Queue
from queue import Empty, Full

def create_queue():
    return Queue()

def enqueue(queue, item):
    try:
        queue.put(item, timeout=1)  # Add timeout to prevent deadlocks
    except Full:
        print("Queue is full. Unable to enqueue item.")

def dequeue(queue):
    try:
        return queue.get(timeout=1)  # Add timeout to prevent indefinite blocking
    except Empty:
        print("Queue is empty. Unable to dequeue item.")
        return None
