import os
import time
import signal
import logging
import threading
from multiprocessing import Event

from utils.shared_memory import SharedMemory

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("lights")

class TrafficLights:
    def __init__(self, shared_memory: SharedMemory, shutdown_flag):
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self._shutdown_called = False
        # Write own PID for signal communication
        with open("lights.pid", "w") as f:
            f.write(str(os.getpid()))
        # Set initial light states
        self.shared_memory.set_light("N", "GREEN")
        self.shared_memory.set_light("S", "GREEN")
        self.shared_memory.set_light("E", "RED")
        self.shared_memory.set_light("W", "RED")
        signal.signal(signal.SIGUSR1, self.handle_priority_signal)
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        if not self._shutdown_called:
            self.handle_shutdown()

    def handle_priority_signal(self, signum, frame):
        thread = threading.Thread(target=self.handle_emergency_mode, daemon=True)
        thread.start()

    def handle_emergency_mode(self) -> None:
        direction = self.shared_memory.get_state("priority_direction")
        if direction in ["N", "S", "E", "W"]:
            self.set_single_green(direction)

    def set_single_green(self, direction: str) -> None:
        self.shared_memory.set_priority_mode(direction)
        for d in ["N", "S", "E", "W"]:
            self.shared_memory.set_light(d, "GREEN" if d == direction else "RED")
        logger.info(f"Emergency mode: Only {direction} is GREEN")
        start_time = time.time()
        emergency_duration = 5  # seconds
        while time.time() - start_time < emergency_duration:
            if self.shutdown_flag.is_set():
                break
            time.sleep(0.1)
        self.shared_memory.reset_priority_mode()

    def normal_operation(self) -> None:
        phase_duration = 30
        current_road = "NS"
        while not self.shutdown_flag.is_set():
            if not self.shared_memory.in_priority_mode():
                for d in ["N", "S", "E", "W"]:
                    if current_road == "NS":
                        self.shared_memory.set_light(d, "GREEN" if d in ["N", "S"] else "RED")
                    else:
                        self.shared_memory.set_light(d, "GREEN" if d in ["E", "W"] else "RED")
                logger.info(f"{current_road} road ➔ GREEN")
                start_time = time.time()
                while time.time() - start_time < phase_duration and not self.shutdown_flag.is_set():
                    time.sleep(0.1)
                current_road = "WE" if current_road == "NS" else "NS"
            else:
                time.sleep(0.1)

    def handle_shutdown(self) -> None:
        self._shutdown_called = True
        logger.info("🔴 Lights shutting down")
        self.shutdown_flag.set()
        try:
            if os.path.exists("lights.pid"):
                os.remove("lights.pid")
        except Exception as e:
            logger.error(f"Error removing PID file: {e}")

    def run(self) -> None:
        try:
            self.normal_operation()
        except KeyboardInterrupt:
            self.handle_shutdown()
        finally:
            self.handle_shutdown()

if __name__ == "__main__":
    from multiprocessing import Manager, Event
    from multiprocessing.managers import SyncManager
    manager: SyncManager = Manager()
    shutdown_flag = Event()
    sm = SharedMemory(manager)
    lights = TrafficLights(sm, shutdown_flag)
    try:
        lights.run()
    except KeyboardInterrupt:
        shutdown_flag.set()
