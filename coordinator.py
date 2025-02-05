import time
import json
import socket
import threading
import logging
from queue import Empty
from multiprocessing import Event, Manager
from utils.shared_memory import SharedMemory

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("coordinator")

class Coordinator:
    def __init__(self, queues, shared_memory: SharedMemory, shutdown_flag):
        self.queues = queues
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self.intersection_lock = shared_memory.lock

    def process_vehicle(self, vehicle: dict) -> None:
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
            logger.info(event_msg)  # Log when a vehicle is processed
        # supposed to hold the vehicle in shared memory so the display can show it but does not really help
        time.sleep(4)
        with self.intersection_lock:
            self.shared_memory.update_state("current_vehicle", None)

    def process_queues(self) -> None:
        while not self.shutdown_flag.is_set():
            processed_vehicle = False
            for direction in ["N", "S", "E", "W"]:
                try:
                    vehicle = self.queues[direction].get_nowait()
                    light_state = self.shared_memory.get_light_state()
                    logger.info(f"Processing vehicle: {vehicle}")  # Log when a vehicle is retrieved
                    if vehicle.get("priority", False):
                        logger.warning(f"🚑 EMERGENCY VEHICLE {vehicle['id']} FORCING PASSAGE")
                        self.process_vehicle(vehicle)
                        processed_vehicle = True
                        break
                    elif light_state.get(direction) == "GREEN":
                        logger.info(f"🟢 Vehicle {vehicle['id']} proceeding {vehicle.get('turn','')}")
                        self.process_vehicle(vehicle)
                        processed_vehicle = True
                        break
                    else:
                        wait_msg = f"Vehicle {vehicle['id'][:8]} from {vehicle['source']} waiting at RED light."
                        self.shared_memory.append_event_log(wait_msg)
                        logger.info(f"🔴 {wait_msg}")
                        time.sleep(2)  # pause so the waiting event is visible
                        self.queues[direction].put(vehicle)
                except Empty:
                    continue
            if not processed_vehicle:
                time.sleep(0.5)


    def run(self) -> None:
        logger.info("Coordinator starting.")
        while not self.shutdown_flag.is_set():
            self.process_queues()
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
    manager = Manager()
    queues = {d: manager.Queue() for d in ["N", "S", "E", "W"]}
    shutdown_flag = Event()
    shared_memory = SharedMemory(manager)

    coordinator = Coordinator(queues, shared_memory, shutdown_flag)
    display_server = DisplayServer(queues, shared_memory, shutdown_flag)

    # Start the display server in a separate thread
    threading.Thread(target=display_server.run, daemon=True).start()

    # Start the coordinator in the main thread
    try:
        coordinator.run()
    except Exception as e:
        logger.error(f"Coordinator crashed: {e}")
        