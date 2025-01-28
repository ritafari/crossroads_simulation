from multiprocessing import Process, Queue, Event
from utils.shared_memory import SharedMemory
from utils.signals import SignalHandler
from traffic.normal_traffic import normal_traffic_gen
from traffic.priority_traffic import priority_traffic_gen
from traffic.coordinator import coordinator_server
from traffic.lights import Lights
<<<<<<< HEAD
from traffic.display import display_client
import time
import logging
=======
from traffic.display import CrossroadsDisplay

>>>>>>> 0ec41fb0b287ebceffdb7febe182c8442d0c5c31

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def main():
    # Initialize shared memory and signal handler
    shared_memory = SharedMemory()
    signal_handler = SignalHandler()
    shutdown_event = Event()  # For graceful shutdown

    # Create one queue per direction
    queues = {
        "S": Queue(),
        "N": Queue(),
        "W": Queue(),
        "E": Queue(),
    }

    # Initialize the lights process
    lights = Lights(shared_memory, signal_handler)

    # Create processes for the components
    processes = [
        Process(target=coordinator_server, args=(queues, shared_memory)),
        Process(target=display_client),  # No additional args needed
        Process(target=normal_traffic_gen, args=(queues, 2)),  # Interval = 2 seconds
        Process(target=priority_traffic_gen, args=(queues, signal_handler, 5)),  # Interval = 5 seconds
        Process(target=lights.run),  # Run the lights logic
    ]

    try:
        # Start all processes
        for process in processes:
            process.start()
            logging.info(f"Started process: {process.name}")

<<<<<<< HEAD
        # Monitor processes for any unexpected terminations
        while not shutdown_event.is_set():
            for process in processes:
                if not process.is_alive():
                    logging.error(f"Process {process.name} has terminated unexpectedly. Shutting down...")
                    shutdown_event.set()
                    break
            time.sleep(1)
=======
        # Start the display client in a thread
        print("Starting display client...")
        display_thread = threading.Thread(target=CrossroadsDisplay)  # No args required
        display_thread.start()
>>>>>>> 0ec41fb0b287ebceffdb7febe182c8442d0c5c31

    except Exception as e:
        logging.error(f"Error in main: {e}")
        shutdown_event.set()

    finally:
        # Terminate all processes cleanly
        for process in processes:
            process.terminate()
            process.join()
        logging.info("All processes terminated. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Shutting down...")
