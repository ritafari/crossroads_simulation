#!/usr/bin/env python3
import time
from multiprocessing import Manager
from multiprocessing.managers import SyncManager
from utils.shared_memory import SharedMemory

def main():
    # Create a single Manager instance.
    manager: SyncManager = Manager()
    
    # Instantiate the SharedMemory object.
    shared_mem = SharedMemory(manager)
    
    # Test 1: Verify initial lights state.
    lights_initial = shared_mem.get_light_state()
    print("Initial lights state:", lights_initial)
    # Expected: {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"}
    
    # Test 2: Change a light and verify update.
    shared_mem.set_light("N", "RED")
    lights_updated = shared_mem.get_light_state()
    print("Updated lights state after setting N to RED:", lights_updated)
    # Expected: "N" should now be "RED"
    
    # Test 3: Update a general state key.
    shared_mem.update_state("current_vehicle", {"id": "veh123", "source": "E", "destination": "W"})
    current_vehicle = shared_mem.get_state("current_vehicle")
    print("Current vehicle state:", current_vehicle)
    # Expected: current_vehicle should be {"id": "veh123", "source": "E", "destination": "W"}
    
    # Test 4: Check priority mode.
    shared_mem.set_priority_mode("S")
    print("Priority mode (should be True):", shared_mem.in_priority_mode())
    print("Priority direction (should be S):", shared_mem.get_state("priority_direction"))
    
    shared_mem.reset_priority_mode()
    print("Priority mode after reset (should be False):", shared_mem.in_priority_mode())
    
    # Test 5: Append event logs and verify trimming.
    for i in range(7):
        event_msg = f"Event {i+1}"
        shared_mem.append_event_log(event_msg)
        time.sleep(0.1)  # slight delay to get different timestamps
    
    # Retrieve and print event logs.
    event_logs = shared_mem.get_state("event_logs")
    print("Event logs (should contain the last 5 events):")
    for event in event_logs:
        print(event)
    
    # Test 6: Get a non-existent key.
    non_existent = shared_mem.get_state("non_existent_key")
    print("Non-existent key (should be None):", non_existent)
    
if __name__ == "__main__":
    main()
