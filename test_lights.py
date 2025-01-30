import time
from multiprocessing import Process
from utils.shared_memory import SharedMemory
from utils.signals import SignalHandler
from traffic.lights import Lights

# Mock shared memory for testing
class MockSharedMemory(SharedMemory):
    def __init__(self):
        super().__init__()
        self.state = {"S": "RED", "N": "RED", "W": "RED", "E": "RED"}  # Initial state

    def update_state(self, key, value):
        """Print updates to simulate shared memory state changes."""
        super().update_state(key, value)
        print(f"Shared memory updated: {key} = {value}")


# Mock signal handler for testing
class MockSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

"""
# Simulate vehicles and priority signals
def simulate_priority_and_normal_cycle(signal_handler):
    time.sleep(5)
    print("\n[Simulation] Priority vehicle detected on 'N' direction.")
    signal_handler.notify_priority({"source": "N"})

    time.sleep(15)
    print("\n[Simulation] Clearing priority signal. Resuming normal cycling.")
    signal_handler.reset_priority_signal()

# Test function
def test_priority_and_normal_cycle():
    # Initialize mock shared memory and signal handler
    shared_memory = MockSharedMemory()
    signal_handler = MockSignalHandler()

    # Initialize Lights instance
    lights = Lights(shared_memory, signal_handler)

    # Start testing
    print("=== Testing Priority and Normal Cycling ===")
    print("Initial light state:", shared_memory.state)

    # Simulate priority signal and normal cycle in a separate thread
    import threading
    threading.Thread(target=simulate_priority_and_normal_cycle, args=(signal_handler,)).start()

    # Run the lights logic
    try:
        lights.run()
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
"""

def simulate_priority_signals(signal_handler):
    """Simulate multiple priority signals."""
    vehicles = [{"source": "N"}, {"source": "E"}, {"source": "W"}, {"source": "S"}]
    for vehicle in vehicles:
        signal_handler.notify_priority(vehicle)
        print(f"Priority signal added for: {vehicle['source']}")
        time.sleep(1)  # Simulate a delay between signals

def run_lights(shared_memory, signal_handler):
    """Run the lights system."""
    lights = Lights(shared_memory, signal_handler)
    lights.run()

if __name__ == "__main__":
    # Create shared memory and signal handler
    signal_handler = SignalHandler()
    shared_memory = MockSharedMemory()  # Replace with your shared memory implementation

    # Start the lights system in a separate process
    lights_process = Process(target=run_lights, args=(shared_memory, signal_handler))
    lights_process.start()

    # Simulate priority signals in another process
    priority_process = Process(target=simulate_priority_signals, args=(signal_handler,))
    priority_process.start()

    # Wait for the priority process to finish
    priority_process.join()

    # Terminate the lights process
    lights_process.terminate()