import os
from multiprocessing import Manager
from utils.signals import SignalHandler

def main():
    # Use the current process PID as a dummy lights_pid.
    # On Linux, /proc/<pid> should exist for the current process.
    current_pid = os.getpid()
    
    # Create a single Manager instance.
    manager = Manager()
    
    # Instantiate the SignalHandler with the current PID.
    sh = SignalHandler(current_pid, manager)
    
    # Create a sample vehicle. Note that the vehicle should contain a 'source' key.
    sample_vehicle = {
        "id": "veh001",
        "source": "n"  # Lowercase intentionally; the SignalHandler will convert to uppercase.
    }
    
    # Call notify_priority to simulate sending a signal.
    sh.notify_priority(sample_vehicle)
    
    # Retrieve and print the priority direction.
    pd = sh.get_priority_direction()
    print("Priority direction after notify_priority:", pd)
    
    # Check the signal_received flag.
    print("Signal received flag (should be True):", sh.signal_received.value)
    
    # Call acknowledge_signal to reset the flag.
    sh.acknowledge_signal()
    print("Signal received flag after acknowledge (should be False):", sh.signal_received.value)

if __name__ == "__main__":
    main()
