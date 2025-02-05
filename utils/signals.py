import os
import signal
import logging
from multiprocessing import Manager, Value
from ctypes import c_bool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("signals")

class SignalHandler:
    def __init__(self, lights_pid: int):
        self.lights_pid = lights_pid
        manager = Manager()
        self.priority_direction = manager.Value('c', b' ')
        self.signal_received = Value(c_bool, False)

    def notify_priority(self, vehicle: dict) -> None:
        try:
            source = vehicle['source'].upper()
            if source not in ['N', 'S', 'E', 'W']:
                raise ValueError("Invalid source direction")
            self.priority_direction.value = source.encode('utf-8')
            self.signal_received.value = True
            os.kill(self.lights_pid, signal.SIGUSR1)
            logger.info(f"Priority signal sent for direction {source}")
        except KeyError as e:
            logger.error(f"Missing vehicle property: {str(e)}")
        except ValueError as e:
            logger.error(f"Invalid direction: {str(e)}")

    def get_priority_direction(self) -> str:
        return self.priority_direction.value.decode('utf-8')

    def acknowledge_signal(self) -> None:
        self.signal_received.value = False
