# just an example 
import threading
from queue import Queue
from utils.shared_memory import SharedMemory
from utils.signals import SignalHandler
from traffic.normal_traffic import normal_traffic_gen
from traffic.priority_traffic import priority_traffic_gen
from traffic.coordinator import coordinator_server
from traffic.lights import Lights
from traffic.display import display_client 

""""
def coordinator_server(queues, lights, shared_memory):
    # Placeholder for the coordinator server logic
    pass

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
    # Initialize shared memory, signal handler, and queues
    shared_memory = SharedMemory()
    signal_handler = SignalHandler()
    queues = {"S": Queue(), "N": Queue(), "W": Queue(), "E": Queue()}

    # Initialize the lights process
    lights = Lights(shared_memory, signal_handler)

    try:
        # Start the coordinator server in a thread
        print("Starting coordinator server...")
        server_thread = threading.Thread(target=coordinator_server, args=(queues, lights, shared_memory))
        server_thread.start()

        # Start the display client in a thread
        print("Starting display client...")
        display_thread = threading.Thread(target=display_client)  # No args required
        display_thread.start()

        # Start normal and priority traffic generators
        print("Starting normal traffic generator...")
        normal_thread = threading.Thread(target=normal_traffic_gen, args=(queues, 2))  # Interval = 2 seconds
        normal_thread.start()

        print("Starting priority traffic generator...")
        priority_thread = threading.Thread(target=priority_traffic_gen, args=(queues, signal_handler, 5))  # Interval = 5 seconds
        priority_thread.start()

        # Join threads to prevent the program from exiting prematurely
        server_thread.join()
        display_thread.join()
        normal_thread.join()
        priority_thread.join()
    except Exception as e:
        print(f"Error in main: {e}")
