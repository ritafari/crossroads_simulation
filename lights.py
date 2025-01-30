import os
import time
import signal
import logging
from multiprocessing import Event

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("lights")

class TrafficLights:
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory
        self.running = Event()
        self.running.set()
        self._shutdown_called = False

        with open("lights.pid", "w") as f:
            f.write(str(os.getpid()))
        
        # Set initial state
        self.shared_memory.set_light("N", "GREEN")
        self.shared_memory.set_light("S", "GREEN")

        # Signal handlers
        signal.signal(signal.SIGUSR1, self.handle_priority_signal)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        if not self._shutdown_called:
            self.handle_shutdown()

    def handle_priority_signal(self, signum, frame):
        direction = self.shared_memory.get_state("priority_direction")
        if direction in ["N", "S", "E", "W"]:
            self.set_single_green(direction)

    def set_single_green(self, direction):
        self.shared_memory.set_priority_mode(direction)
        for d in ["N", "S", "E", "W"]:
            self.shared_memory.set_light(d, "GREEN" if d == direction else "RED")
        time.sleep(5)
        self.shared_memory.reset_priority_mode()

    def normal_operation(self):
        phase_duration = 30
        current_road = "NS"
        while self.running.is_set():
            if not self.shared_memory.in_priority_mode():
                for d in ["N", "S", "E", "W"]:
                    self.shared_memory.set_light(d, "GREEN" if d in current_road else "RED")
                logger.info(f"{current_road} road ➔ GREEN")
                start_time = time.time()
                while time.time() - start_time < phase_duration and self.running.is_set():
                    time.sleep(0.1)
                current_road = "WE" if current_road == "NS" else "NS"

    def handle_shutdown(self):
        self._shutdown_called = True
        logger.info("🔴 Lights shutting down")
        self.running.clear()
        try:
            if os.path.exists("lights.pid"):
                os.remove("lights.pid")
        except Exception as e:
            pass  # Avoid spamming errors

    def run(self):
        try:
            self.normal_operation()
        except KeyboardInterrupt:
            self.handle_shutdown()
        finally:
            self.handle_shutdown()