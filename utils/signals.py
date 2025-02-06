import os
import signal
import logging
from multiprocessing import Value
from multiprocessing.managers import BaseManager as Manager
from ctypes import c_bool, c_char_p

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signals")

class SignalHandler:
    def __init__(self, lights_pid: int, manager: Manager): 
        """
        Initializes the SignalHandler with a given lights process ID and a shared memory manager.
        :param lights_pid: Process ID of the traffic lights controller.
        :param manager: Shared memory manager for inter-process communication.
        """
        self.lights_pid = lights_pid
        self.priority_direction = manager.Value(c_char_p, b' ')  # Stores direction as a string
        self.signal_received = manager.Value(c_bool, False)  # Flag for priority signal
        signal.signal(signal.SIGUSR1, self.handle_priority_signal)

    def notify_priority(self, vehicle: dict) -> None:
        """
        Sends a priority signal to the traffic lights controller based on the vehicle's direction.
        :param vehicle: Dictionary containing vehicle information with a 'source' key.
        """
        try:
            source = vehicle.get('source', '').upper()
            if source not in ['N', 'S', 'E', 'W']:
                raise ValueError("Invalid source direction")
            
            self.priority_direction.value = source.encode('utf-8')

            # Ensure the process exists before sending a signal
            if not os.path.exists(f"/proc/{self.lights_pid}"):  # Works on Linux
                raise OSError(f"Process {self.lights_pid} not found")
            
            os.kill(self.lights_pid, signal.SIGUSR1)    #Ensures os.kill() only runs if process exists (prevents crashes).
            logger.info(f"🚨 Priority signal sent for direction {source}")
        
        except (KeyError, ValueError, OSError) as e:
            logger.error(f"Signal error: {e}")

    def handle_priority_signal(self, signum, frame):
        # Update the flag and log a message without causing the default output.
        self.signal_received.value = True
        logger.debug("Received SIGUSR1: Emergency signal processed.")

    def get_priority_direction(self) -> str:
        """
        Retrieves the currently stored priority direction.
        :return: Priority direction as a string.
        """
        return self.priority_direction.value.decode('utf-8')

    def acknowledge_signal(self) -> None:
        """
        Resets the signal_received flag after handling an emergency signal.
        """
        self.signal_received.value = False
