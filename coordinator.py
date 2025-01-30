# coordinator.py
import time
import socket
import json
import logging
from queue import Empty
from multiprocessing import Queue
from utils.shared_memory import SharedMemory
import threading

logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("coordinator")

class Coordinator:
    def __init__(self, queues, shared_memory, shutdown_flag):
        self.queues = queues
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self.intersection_lock = shared_memory.lock  # Use shared lock for atomic operations

    def process_vehicle(self, vehicle):
        """Handle vehicle movement according to traffic rules"""
        with self.intersection_lock:
            # Update shared memory with current vehicle
            self.shared_memory.update_state("current_vehicle", vehicle)
            
            logger.info(
                f"Processing {'PRIORITY' if vehicle['priority'] else ''} "
                f"vehicle {vehicle['id'][:8]} from {vehicle['source']} "
                f"to {vehicle['destination']} (turn: {vehicle.get('turn', '')})"
            )

    def process_queues(self):
        """Process all queues with proper priority handling"""
        # First pass: Emergency vehicles
        for direction in ["N", "S", "E", "W"]:
            try:
                vehicle = self.queues[direction].get_nowait()
                if vehicle["priority"]:
                    self.process_vehicle(vehicle)
                    return  # Prioritize single vehicle processing per cycle
                else:
                    self.queues[direction].put(vehicle)
            except Empty:
                continue

        # Second pass: Right turns
        for direction in ["N", "S", "E", "W"]:
            try:
                vehicle = self.queues[direction].get_nowait()
                if vehicle.get("turn") == "right":
                    self.process_vehicle(vehicle)
                    return
                else:
                    self.queues[direction].put(vehicle)
            except Empty:
                continue

        # Third pass: Normal green light vehicles
        light_state = self.shared_memory.get_light_state()
        for direction in ["N", "S", "E", "W"]:
            try:
                vehicle = self.queues[direction].get_nowait()
                if light_state.get(direction) == "GREEN":
                    self.process_vehicle(vehicle)
                    return
                else:
                    self.queues[direction].put(vehicle)
            except Empty:
                continue

    def run(self):
        """Main control loop"""
        logger.info("Starting coordinator")
        while not self.shutdown_flag.is_set():
            self.process_queues()
            time.sleep(0.1)

class DisplayServer:
    def __init__(self, queues, shared_memory, shutdown_flag, host="127.0.0.1", port=65432):
        self.queues = queues
        self.shared_memory = shared_memory
        self.shutdown_flag = shutdown_flag
        self.host = host  # Correct order
        self.port = port
        self.running = True

    def generate_status(self):
        """Atomic status generation"""
        return {
            "lights": self.shared_memory.get_light_state(),
            "queues": {d: self.queues[d].qsize() for d in ["N", "S", "E", "W"]},
            "current_vehicle": self.shared_memory.get_state("current_vehicle")
        }

    def handle_client(self, conn):
        """Send continuous updates"""
        try:
            while self.running:
                status = json.dumps(self.generate_status()).encode()
                try:
                    conn.sendall(status + b'\n')  # Add message separator
                    time.sleep(0.2)  # Faster updates
                except (BrokenPipeError, ConnectionResetError):
                    break
        finally:
            conn.close()

    def run(self):
        """Server with graceful shutdown"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.settimeout(1)  # Allow periodic shutdown checks
            s.listen()
            logger.info(f"Display server ready on {self.host}:{self.port}")
            
            while self.running:
                try:
                    conn, addr = s.accept()
                    logger.info(f"New display connection from {addr}")
                    thread = threading.Thread(
                        target=self.handle_client, 
                        args=(conn,),
                        daemon=True  # for clean exits
                    )
                    thread.start()
                except socket.timeout:
                    continue
            

if __name__ == "__main__":
    from multiprocessing import Manager

    manager = Manager()
    queues = manager.dict({
        "N": manager.Queue(),
        "S": manager.Queue(),
        "E": manager.Queue(),
        "W": manager.Queue()
    })
    
    sm = SharedMemory()
    
    coordinator = Coordinator(queues, sm)
    display = DisplayServer(queues, sm)
    
    from multiprocessing import Process
    p1 = Process(target=coordinator.run)
    p2 = Process(target=display.run)
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()