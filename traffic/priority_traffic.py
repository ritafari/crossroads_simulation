# Functions and processes for priority traffic generation

import time
import random
import uuid  # For generating unique vehicle IDs

# List of possible directions
DIRECTIONS = ["S", "N", "W", "E"]

def create_vehicle(vehicle_type):
    """Creates a vehicle with randomized attributes."""
    source = random.choice(DIRECTIONS)
    destination = random.choice([d for d in DIRECTIONS if d != source])  # Ensure destination is different from source
    return {
        "id": str(uuid.uuid4()),  # Unique identifier for the vehicle
        "type": vehicle_type,
        "source": source,
        "destination": destination,
        "timestamp": time.time(),  # Optional: timestamp for when the vehicle is generated
    }

def priority_traffic_gen(queues, signal_handler, interval):
    """
    Generate priority traffic and enqueue it into the appropriate queue.
    Sends a signal to the system to notify about the priority vehicle.
    """
    while True:
        # Create a priority vehicle
        vehicle = create_vehicle("priority")
        # Add the vehicle to the queue corresponding to its source direction
        queues[vehicle["source"]].put(vehicle)
        # Notify the signal handler about the priority vehicle
        signal_handler.notify_priority(vehicle)
        print(f"Generated PRIORITY vehicle {vehicle['id']} from {vehicle['source']} to {vehicle['destination']}")
        # Wait for the specified interval
        time.sleep(interval)


"""
HOW TO USE THE CODE:
1. Initialize message queue
from queue import Queue
from utils.signals import SignalHandler

# Create one queue per direction
queues = {
    "S": Queue(),
    "N": Queue(),
    "W": Queue(),
    "E": Queue(),
}

# Initialize the signal handler
signal_handler = SignalHandler()

2. Start the priority_traffic_gen process
import threading

# Start the priority traffic generator in a separate thread
priority_thread = threading.Thread(target=priority_traffic_gen, args=(queues, signal_handler, 5))  # Interval = 5 seconds
priority_thread.start()

3. Monitor the queues for incoming vehicles
while True:
    for direction, queue in queues.items():
        if not queue.empty():
            vehicle = queue.get()
            print(f"Processing PRIORITY vehicle {vehicle['id']} from {vehicle['source']} to {vehicle['destination']}")
    time.sleep(1)

OUTPUT EXAMPLE
Generated PRIORITY vehicle a12b34c5-d678-90ef-1234-56789abcd012 from N to W
Priority vehicle detected from N to W
Processing PRIORITY vehicle a12b34c5-d678-90ef-1234-56789abcd012 from N to W
"""