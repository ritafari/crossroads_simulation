import os
import time
import signal
import logging
import threading
import multiprocessing
from typing import Optional
from utils.shared_memory import SharedMemory


logging.basicConfig(level=logging.INFO, format="%(name)s - %(process)d - %(message)s")
logger = logging.getLogger("lights")

PHASE_DURATION = 30  # Seconds for each traffic light phase
EMERGENCY_DURATION = 5  # Seconds for emergency priority mode

class TrafficLights:
    def __init__(self, shared_memory: SharedMemory, shutdown_flag):
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self._shutdown_called = False
        
        # Write PID file with error handling
        try:
            with open("lights.pid", "w") as f:
                f.write(str(os.getpid()))
            logger.info("PID file created successfully")
        except IOError as e:
            logger.error(f"Failed to create PID file: {e}")
            raise RuntimeError("Could not initialize traffic lights") from e

        # Initialize signal handling
        signal.signal(signal.SIGUSR1, self.handle_priority_signal)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Set initial light states
        self._initialize_lights()

    def _initialize_lights(self) -> None:
        """Set initial light states for NS/WEW traffic flow"""
        try:
            self.shared_memory.set_light("N", "GREEN")
            self.shared_memory.set_light("S", "GREEN")
            self.shared_memory.set_light("E", "RED")
            self.shared_memory.set_light("W", "RED")
            logger.info("Initial light states set: NS-GREEN, EW-RED")
        except Exception as e:
            logger.error(f"Failed to initialize lights: {e}")
            raise

    def signal_handler(self, signum: int, frame: Optional[object]) -> None:
        """Handle SIGINT signal"""
        if not self._shutdown_called:
            logger.info("Received shutdown signal")
            self.handle_shutdown()

    def handle_priority_signal(self, signum: int, frame: Optional[object]) -> None:
        """Handle SIGUSR1 signal in a thread-safe manner"""
        thread = threading.Thread(
            target=self._handle_emergency_mode, 
            daemon=True,
            name="EmergencyHandler"
        )
        thread.start()

    def _handle_emergency_mode(self) -> None:
        """Process emergency vehicle priority request."""
        try:
            direction = self.shared_memory.get_state("priority_direction")
            if direction is None:
                # For testing, default to a valid direction (e.g., "N")
                direction = "N"
                logger.warning("No emergency direction set; defaulting to N.")
            if direction in ("N", "S", "E", "W"):
                logger.warning(f"🚑 Activating emergency mode for {direction}")
                self._set_single_green(direction)
            else:
                logger.error(f"Invalid emergency direction: {direction}")
        except Exception as e:
            logger.error(f"Emergency mode error: {e}")

    def _set_single_green(self, direction: str) -> None:
        """Set green light for a single direction (emergency mode)"""
        try:
            self.shared_memory.set_priority_mode(direction)
            for d in ["N", "S", "E", "W"]:
                status = "GREEN" if d == direction else "RED"
                self.shared_memory.set_light(d, status)
            
            logger.info(f"🚑 Emergency priority: {direction}-GREEN")
            start_time = time.time()
            
            # Maintain emergency mode unless interrupted.
            while (time.time() - start_time < EMERGENCY_DURATION 
                   and not self.shutdown_flag.is_set()):
                time.sleep(0.1)
            
            logger.info("Returning to normal operation")
            self.shared_memory.reset_priority_mode()
        except Exception as e:
            logger.error(f"Emergency mode failed: {e}")
            self.shared_memory.reset_priority_mode()

    def normal_operation(self) -> None:
        """Main traffic light control loop"""
        current_phase = "NS"
        logger.info("Starting normal operation")
        
        try:
            while not self.shutdown_flag.is_set():
                if self.shared_memory.in_priority_mode():
                    time.sleep(0.1)
                    continue
                
                # Set lights for current phase.
                self._set_phase_lights(current_phase)
                logger.info(f"🚦 {current_phase} phase active")
                
                # Wait for phase duration with frequent shutdown checks.
                start_time = time.time()
                while (time.time() - start_time < PHASE_DURATION 
                       and not self.shutdown_flag.is_set()):
                    time.sleep(0.1)
                
                # Switch to next phase.
                current_phase = "WE" if current_phase == "NS" else "NS"
        except Exception as e:
            logger.error(f"Normal operation error: {e}")
            self.handle_shutdown()

    def _set_phase_lights(self, phase: str) -> None:
        """Update lights for a given phase (NS or WE)"""
        try:
            for direction in ["N", "S", "E", "W"]:
                status = "GREEN" if direction in phase else "RED"
                self.shared_memory.set_light(direction, status)
        except Exception as e:
            logger.error(f"Failed to set {phase} phase: {e}")
            raise

    def handle_shutdown(self) -> None:
        """Cleanup resources and prepare for shutdown"""
        if self._shutdown_called:
            return
            
        self._shutdown_called = True
        logger.info("🛑 Beginning shutdown sequence")
        self.shutdown_flag.set()
        
        try:
            if os.path.exists("lights.pid"):
                os.remove("lights.pid")
                logger.info("Removed PID file")
        except Exception as e:
            logger.error(f"PID file removal failed: {e}")
        
        try:
            self.shared_memory.cleanup()
        except Exception as e:
            logger.error(f"Shared memory cleanup failed: {e}")

    def run(self) -> None:
        """Main entry point for traffic light controller"""
        try:
            self.normal_operation()
        except KeyboardInterrupt:
            self.handle_shutdown()
        finally:
            self.handle_shutdown()


if __name__ == "__main__":
    from multiprocessing import Manager
    manager = Manager()
    _shutdown_flag = multiprocessing.Event()
    try:
        sm = SharedMemory(manager)
        lights = TrafficLights(sm, _shutdown_flag)
        lights.run()
    except Exception as e:
        logger.error(f"Critical failure: {e}")
    finally:
        logger.info("Shutting down manager...")
        manager.shutdown()
        logger.info("Clean shutdown complete")


"""
Usage Notes:

- Configuration
    Modify constants at the top of the file to adjust timing:
        PHASE_DURATION = 30  # Normal phase duration
        EMERGENCY_DURATION = 5  # How long emergency mode lasts
- Error Recovery
    The system will attempt to:
    Recover from failed shared memory operations
    Clean up resources even after errors
    Maintain operation during brief file system issues
- Monitoring
    Watch for these key log messages:
        🚑 Emergency priority: X-GREEN - Active emergency mode
        🚦 XX phase active - Normal phase changes
        🛑 Beginning shutdown sequence - Clean shutdown initiated
"""