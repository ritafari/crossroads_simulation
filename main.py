# just an example 

import threading
from queue import Queue
from utils.signals import SignalHandler
from utils.shared_memory import SharedMemory
from traffic.normal_traffic import normal_traffic_gen
from traffic.priority_traffic import priority_traffic_gen
from traffic.lights import Lights


""""
def main():
    # Initialize shared memory
    shared_memory = SharedMemory()

    # Initialize signal handler
    signal_handler = SignalHandler()

    # Create one queue per direction
    queues = {
        "S": Queue(),
        "N": Queue(),
        "W": Queue(),
        "E": Queue(),
    }

    # Initialize the lights process
    lights = Lights(shared_memory, signal_handler)

    # Start normal traffic generator thread
    normal_thread = threading.Thread(target=normal_traffic_gen, args=(queues, 2))  # Interval = 2 seconds
    normal_thread.start()

    # Start priority traffic generator thread
    priority_thread = threading.Thread(target=priority_traffic_gen, args=(queues, signal_handler, 5))  # Interval = 5 seconds
    priority_thread.start()

    # Start the coordinator thread
    coordinator_thread = threading.Thread(target=coordinator, args=(queues, lights, shared_memory))
    coordinator_thread.start()

    # Start the lights thread
    lights_thread = threading.Thread(target=lights.run)  # Assuming `lights.run()` manages light logic
    lights_thread.start()

    # Join threads to keep the program running
    normal_thread.join()
    priority_thread.join()
    coordinator_thread.join()
    lights_thread.join()

if __name__ == "__main__":
    main()
"""


def main():
    shared_memory = SharedMemory()
    signal_handler = SignalHandler()
    queues = {"S": Queue(), "N": Queue(), "W": Queue(), "E": Queue()}
    lights = Lights(shared_memory, signal_handler)

    # Debug: Print when threads are starting
    print("Starting coordinator server...")
    server_thread = threading.Thread(target=coordinator_server, args=(queues, lights, shared_memory))
    server_thread.start()

    print("Starting display client...")
    display_thread = threading.Thread(target=display_client)
    display_thread.start()

    print("Starting normal traffic generator...")
    normal_thread = threading.Thread(target=normal_traffic_gen, args=(queues, 2))  # Interval = 2s
    normal_thread.start()

    print("Starting priority traffic generator...")
    priority_thread = threading.Thread(target=priority_traffic_gen, args=(queues, signal_handler, 5))  # Interval = 5s
    priority_thread.start()

    # Join threads
    server_thread.join()
    display_thread.join()
    normal_thread.join()
    priority_thread.join()
