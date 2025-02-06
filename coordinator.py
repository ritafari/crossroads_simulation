import time
import json
import socket
import threading
import logging
from queue import Empty
from multiprocessing import Manager
from utils.shared_memory import SharedMemory

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("coordinator")

class Coordinator:
    def __init__(self, queues, shared_memory: SharedMemory, shutdown_flag):
        self.queues = queues  # Dict: direction -> Queue
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self.intersection_lock = shared_memory.lock

    def process_vehicle(self, vehicle: dict) -> None:
        """
        Process the vehicle synchronously (for debugging).
        In sim spawn a thread for asynchronous processing.
        """
        with self.intersection_lock:
            self.shared_memory.update_state("current_vehicle", vehicle)
            if vehicle.get("priority", False):
                action = "passed through with EMERGENCY clearance"
            else:
                action = "passed through on GREEN light"
            event_msg = (f"Vehicle {vehicle['id'][:8]} "
                        f"({'EMERGENCY' if vehicle.get('priority') else 'normal'}) "
                        f"from {vehicle['source']} to {vehicle['destination']} {action}.")
            self.shared_memory.append_event_log(event_msg)
            logger.info(f"✅ Vehicle processed: {event_msg}")
        # Synchronously wait for 4 seconds (using small intervals).
        sleep_time = 4.0
        elapsed = 0.0
        interval = 0.1
        while elapsed < sleep_time and not self.shutdown_flag.is_set():
            time.sleep(interval)
            elapsed += interval
        with self.intersection_lock:
            self.shared_memory.update_state("current_vehicle", None)


    def process_queue_for_direction(self, direction: str) -> None:
        """
        Continuously process vehicles from a given queue.
        Emergency vehicles are processed in a loop to handle multiple priority vehicles.
        """
        while not self.shutdown_flag.is_set():
            try:
                vehicle = self.queues[direction].get(timeout=0.5)
                light_state = self.shared_memory.get_light_state()
                logger.info(f"Processing vehicle from {direction}: {vehicle}")
                
                if vehicle.get("priority", False):
                    # Process consecutive emergency vehicles in a loop.
                    while True:
                        logger.warning(f"🚑 EMERGENCY VEHICLE {vehicle['id']} FORCING PASSAGE")
                        self.process_vehicle(vehicle)
                        logger.info(f"✅ Emergency vehicle {vehicle['id']} processed.")
                        try:
                            next_vehicle = self.queues[direction].get_nowait()
                            if next_vehicle.get("priority", False):
                                vehicle = next_vehicle  # Process next emergency vehicle.
                            else:
                                self.queues[direction].put(next_vehicle)
                                break
                        except Empty:
                            break
                elif light_state.get(direction) == "GREEN":
                    logger.info(f"🟢 Vehicle {vehicle['id']} allowed to pass ({vehicle.get('turn','')}).")
                    self.process_vehicle(vehicle)
                else:
                    # Debug: log the current light state.
                    current_status = self.shared_memory.get_light_state().get(direction, "RED")
                    logger.debug(f"[DEBUG] Vehicle {vehicle['id'][:8]} in {direction} sees light: {current_status}.")
                    
                    # Log that the vehicle is waiting.
                    wait_msg = f"Vehicle {vehicle['id'][:8]} from {vehicle['source']} waiting at {direction} RED light."
                    self.shared_memory.append_event_log(wait_msg)
                    logger.info(f"⏸️ {wait_msg}")
                    
                    # Wait for up to 5 seconds, logging each second.
                    total_wait = 5
                    for i in range(total_wait):
                        if self.shutdown_flag.is_set():
                            logger.info(f"[DEBUG] Shutdown flag set; breaking waiting loop for vehicle {vehicle['id'][:8]}.")
                            break
                        time.sleep(1)
                        logger.info(f"Waiting for {direction} light: {i+1} second(s) elapsed for vehicle {vehicle['id'][:8]}.")
                    
                    # If shutdown flag is set, do nothing further.
                    if self.shutdown_flag.is_set():
                        continue
                    
                    # After waiting, re-read the light state.
                    current_light = self.shared_memory.get_light_state().get(direction, "RED")
                    if current_light == "GREEN":
                        logger.info(f"Light for {direction} turned GREEN; processing waiting vehicle {vehicle['id'][:8]}.")
                        self.process_vehicle(vehicle)
                    else:
                        # Only requeue if the vehicle has not been processed.
                        if not vehicle.get("processed", False):
                            logger.info(f"Vehicle {vehicle['id'][:8]} still waiting after {total_wait} seconds; requeueing.")
                            self.queues[direction].put(vehicle)
                        else:
                            logger.info(f"Vehicle {vehicle['id'][:8]} already processed; not requeueing.")


            except Empty:
                continue

    def run(self) -> None:
        logger.info("Coordinator starting.")
        # Start a dedicated thread for each directional queue.
        for direction in ["N", "S", "E", "W"]:
            threading.Thread(target=self.process_queue_for_direction, args=(direction,), daemon=True).start()
        # Main loop: wait for shutdown.
        while not self.shutdown_flag.is_set():
            time.sleep(0.1)
        logger.info("Coordinator shutting down.")

class DisplayServer:
    def __init__(self, queues, shared_memory: SharedMemory, shutdown_flag, host="127.0.0.1", port=65432):
        self.queues = queues
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self.host = host
        self.port = port
        self.running = True

    def generate_status(self) -> dict:
        return {
            "lights": self.shared_memory.get_light_state(),
            "queues": {d: self.queues[d].qsize() for d in ["N", "S", "E", "W"]},
            "current_vehicle": self.shared_memory.get_state("current_vehicle"),
            "event_logs": list(self.shared_memory.get_state("event_logs"))
        }

    def handle_client(self, conn: socket.socket) -> None:
        try:
            while self.running and not self.shutdown_flag.is_set():
                status = self.generate_status()
                try:
                    conn.sendall((json.dumps(status) + "\n").encode())
                    time.sleep(0.2)
                except (BrokenPipeError, ConnectionResetError):
                    break
        finally:
            conn.close()

    def run(self) -> None:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.settimeout(1)
            s.listen()
            logger.info(f"Display server ready on {self.host}:{self.port}")
            while self.running and not self.shutdown_flag.is_set():
                try:
                    conn, addr = s.accept()
                    logger.info(f"New display connection from {addr}")
                    threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
                except socket.timeout:
                    continue
            logger.info("Display server shutting down.")

if __name__ == "__main__":
    from multiprocessing import Manager
    manager = Manager()
    queues = {d: manager.Queue() for d in ["N", "S", "E", "W"]}
    shutdown_flag = manager.Event()
    from utils.shared_memory import SharedMemory
    shared_memory = SharedMemory(manager)

    coordinator = Coordinator(queues, shared_memory, shutdown_flag)
    display_server = DisplayServer(queues, shared_memory, shutdown_flag)

    # Start the display server in a separate thread.
    threading.Thread(target=display_server.run, daemon=True).start()

    try:
        coordinator.run()
    except Exception as e:
        logger.error(f"Coordinator crashed: {e}")
