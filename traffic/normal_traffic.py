# Functions and processes for normal traffic generation


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

def normal_traffic_gen(queues, interval):
    """
    Generate normal traffic and enqueue it into the appropriate queue.
    Each queue corresponds to a direction: S, N, W, or E.
    """
    while True:
        # Create a normal vehicle
        vehicle = create_vehicle("normal")
        # Add the vehicle to the queue corresponding to its source direction
        queues[vehicle["source"]].put(vehicle)
        print(f"Generated vehicle {vehicle['id']} from {vehicle['source']} to {vehicle['destination']}")
        # Wait for the specified interval
        time.sleep(interval)


"""
HOW TO USE THE CODE:
1. Initialize message queue
from queue import Queue
# Create one queue per direction
queues = {
    "S": Queue(),
    "N": Queue(),
    "W": Queue(),
    "E": Queue(),
}

2. Start the normal_traffic_gen process
import threading

# Start the normal traffic generator in a separate thread
thread = threading.Thread(target=normal_traffic_gen, args=(queues, 2))  # Interval = 2 seconds
thread.start()

3. Monitor the queues for incoming vehicles
while True:
    for direction, queue in queues.items():
        if not queue.empty():
            vehicle = queue.get()
            print(f"Processing vehicle {vehicle['id']} from {vehicle['source']} to {vehicle['destination']}")
    time.sleep(1)

OUTPUT EXAMPLE
Generated vehicle a12b34c5-d678-90ef-1234-56789abcd012 from S to N
Generated vehicle b98c76d5-e432-10ba-0987-65432fedcba0 from W to E
Processing vehicle a12b34c5-d678-90ef-1234-56789abcd012 from S to N
Processing vehicle b98c76d5-e432-10ba-0987-65432fedcba0 from W to E
"""