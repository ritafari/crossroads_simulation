import time
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager

from coordinator import Coordinator, DisplayServer
from lights import TrafficLights
from normal_traffic import normal_traffic_gen
from priority_traffic import priority_traffic_gen
from utils.message_queues import create_queues
from utils.shared_memory import SharedMemory
from display import main as run_display_client  # Assuming display.py has a main function


def main():
    manager: SyncManager = Manager()
    shutdown_flag = manager.Event()

    # Create shared resources using the same manager
    queues = create_queues(manager)
    shared_memory = SharedMemory(manager)
    
    # Instantiate the simulation components
    coordinator_instance = Coordinator(queues, shared_memory, shutdown_flag)
    display_server_instance = DisplayServer(queues, shared_memory, shutdown_flag)
    lights_instance = TrafficLights(shared_memory, shutdown_flag)
    
    # Create processes for each task in the simulation
    coordinator_process = Process(target=coordinator_instance.run, name="Coordinator")
    display_server_process = Process(target=display_server_instance.run, name="DisplayServer")
    lights_process = Process(target=lights_instance.run, name="TrafficLights")
    normal_traffic_process = Process(target=normal_traffic_gen, args=(queues, 2, shutdown_flag), name="NormalTraffic")
    priority_traffic_process = Process(target=priority_traffic_gen, args=(queues, 5, shutdown_flag), name="PriorityTraffic")
    display_client_process = Process(target=run_display_client, name="DisplayClient")  # Ensure this function works as a process
    
    # List of all processes
    processes = [
        coordinator_process,
        display_server_process,
        lights_process,
        normal_traffic_process,
        priority_traffic_process,
        display_client_process,
    ]
    
    # Start all processes
    for p in processes:
        p.start()

    print("Simulation started. Press Ctrl+C to shut down.")
    
    try:
        while True:
            time.sleep(1)  # Keep the main process running
    except KeyboardInterrupt:
        print("Shutdown signal received. Terminating all processes...")
        shutdown_flag.set()  # Signal all processes to shut down
    
    # Wait for all processes to terminate
    for p in processes:
        p.join()

    print("All processes have been terminated.")


if __name__ == "__main__":
    main()
