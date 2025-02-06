#!/usr/bin/env python3
import time
from multiprocessing import Manager, Process
from multiprocessing.managers import SyncManager

from coordinator import Coordinator, DisplayServer
from lights import TrafficLights
from normal_traffic import normal_traffic_gen
from priority_traffic import priority_traffic_gen 
from utils.message_queues import create_queues
from utils.shared_memory import SharedMemory
from display import main as run_display_client  

def main():
    manager: SyncManager = Manager()
    shutdown_flag = manager.Event()

    # Create shared resources using the same manager.
    queues = create_queues()  
    shared_memory = SharedMemory(manager)
    
    # Instantiate the simulation components.
    coordinator_instance = Coordinator(queues, shared_memory, shutdown_flag)
    display_server_instance = DisplayServer(queues, shared_memory, shutdown_flag)
    lights_instance = TrafficLights(shared_memory, shutdown_flag)
    
    # Create processes for each simulation component.
    coordinator_process = Process(target=coordinator_instance.run, name="Coordinator")
    display_server_process = Process(target=display_server_instance.run, name="DisplayServer")
    lights_process = Process(target=lights_instance.run, name="TrafficLights")
    normal_traffic_process = Process(target=normal_traffic_gen, args=(queues, 10, shutdown_flag), name="NormalTraffic")
    priority_traffic_process = Process(target=priority_traffic_gen, args=(queues, 20, shutdown_flag, manager), name="PriorityTraffic")
    display_client_process = Process(target=run_display_client, name="DisplayClient")
    
    processes = [
        coordinator_process,
        display_server_process,
        lights_process,
        normal_traffic_process,
        priority_traffic_process,
        display_client_process,
    ]
    
    # Start all processes (start display client after a delay).
    for p in processes[:-1]:
        p.start()
    time.sleep(2)
    processes[-1].start()

    print("Simulation started. Press Ctrl+C to shut down.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutdown signal received. Terminating all processes...")
        shutdown_flag.set()
    
    for p in processes:
        p.join()
    
    print("All processes have been terminated.")

if __name__ == "__main__":
    main()
