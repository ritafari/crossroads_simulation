# Unit tests for priority traffic generation

from queue import Queue
import threading
import time
import random
import uuid
from traffic.priority_traffic import priority_traffic_gen

# Test signal handler
class SignalHandler:
    def notify_priority(self, vehicle):
        print(f"Priority vehicle detected from {vehicle['source']} to {vehicle['destination']}")

# Test vehicle creation and generation function
def test_priority_traffic_gen():
    queues = {
        "S": Queue(),
        "N": Queue(),
        "W": Queue(),
        "E": Queue(),
    }

    signal_handler = SignalHandler()

    # Start the priority traffic generator in a separate thread
    priority_thread = threading.Thread(target=priority_traffic_gen, args=(queues, signal_handler, 2))  # Interval = 2 seconds
    priority_thread.daemon = True  # Allows the thread to exit when the main program finishes
    priority_thread.start()

    # Monitor the queues for incoming vehicles
    for _ in range(5):  # Run for a short period to observe vehicle processing
        time.sleep(1)
        for direction, queue in queues.items():
            if not queue.empty():
                vehicle = queue.get()
                print(f"Processing PRIORITY vehicle {vehicle['id']} from {vehicle['source']} to {vehicle['destination']}")

# Test the priority traffic generation
test_priority_traffic_gen()


"""
Example output gen: 
Generated PRIORITY vehicle a12b34c5-d678-90ef-1234-56789abcd012 from N to W
Priority vehicle detected from N to W
Processing PRIORITY vehicle a12b34c5-d678-90ef-1234-56789abcd012 from N to W
"""
