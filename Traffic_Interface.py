import pygame
import socket
import json
import time
import threading
import logging
from multiprocessing import shared_memory, Queue

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("display")

# Pygame Initialization
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Traffic Simulation")

# Load Images
DIRECTIONS = ["N->S", "S->N", "E->W", "W->E"]
VEHICLE_CLASSES = ["car", "bus", "truck"]
PATH = "traffic/{}/{}.jpg".format(DIRECTIONS[0], VEHICLE_CLASSES[0])

BACKGROUND_IMG = pygame.image.load("traffic/crossroads.webp")  # Background intersection image
CAR_IMG = pygame.image.load(PATH)  # Example vehicle image
GREEN_LIGHT_IMG = pygame.image.load("traffic/Signals/greenLight.jpg")
RED_LIGHT_IMG = pygame.image.load("traffic/Signals/redLight.jpg")

# Resize images if needed
CAR_IMG = pygame.transform.scale(CAR_IMG, (50, 30))  # Resize car for better display
GREEN_LIGHT_IMG = pygame.transform.scale(GREEN_LIGHT_IMG, (30, 70))
RED_LIGHT_IMG = pygame.transform.scale(RED_LIGHT_IMG, (30, 70))

# Traffic Light Positions (Assumed fixed)
TRAFFIC_LIGHT_POS = {
    "N": (460, 200),
    "S": (460, 600),
    "E": (730, 400),
    "W": (230, 400)
}

# Vehicle Start Positions (Example values)
VEHICLE_POSITIONS = {
    "N": (500, 50),
    "S": (500, 750),
    "E": (900, 400),
    "W": (50, 400)
}

class TrafficDisplay:
    def __init__(self, shutdown_flag, shared_mem_name, message_queue, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.running = True
        self.shutdown_flag = shutdown_flag
        self.vehicles = []  # Stores vehicle data
        self.message_queue = message_queue

        try:
            # Try attaching to existing shared memory
            self.shared_memory = shared_memory.SharedMemory(name=shared_mem_name)
        except FileNotFoundError:
            # If not found, create it with a fixed size (adjust size as needed)
            self.shared_memory = shared_memory.SharedMemory(name=shared_mem_name, create=True, size=1024)
            print(f"Created new shared memory: {shared_mem_name}")
    
    def draw_traffic_lights(self, lights):
        """Draw traffic lights based on state"""
        for direction, state in lights.items():
            img = GREEN_LIGHT_IMG if state == "GREEN" else RED_LIGHT_IMG
            screen.blit(img, TRAFFIC_LIGHT_POS[direction])
    
    def draw_vehicles(self):
        """Draw all vehicles"""
        for vehicle in self.vehicles:
            x, y = vehicle["pos"]
            screen.blit(CAR_IMG, (x, y))
    
    def update_vehicles(self, vehicles_data):
        """Update vehicle positions"""
        self.vehicles = []  # Clear previous vehicle data
        for direction, count in vehicles_data.items():
            for i in range(count):
                x, y = VEHICLE_POSITIONS[direction]
                y += i * 35  # Stack vehicles vertically
                self.vehicles.append({"pos": (x, y), "direction": direction})
    
    def fetch_shared_memory_data(self):
        """Reads traffic light and vehicle queue state from shared memory."""
        data = json.loads(self.shared_memory.buf[:].tobytes().decode("utf-8"))
        return data
    
    def process_message_queue(self):
        """Processes new messages from the queue."""
        while not self.message_queue.empty():
            message = self.message_queue.get()
            if message:
                traffic_data = json.loads(message)
                self.update_vehicles(traffic_data.get("queues", {}))
    
    def run(self):
        buffer = b""
        while not self.shutdown_flag.is_set():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    while not self.shutdown_flag.is_set():
                        data = s.recv(4096)
                        if not data:
                            break

                        buffer += data
                        while b'\n' in buffer:
                            msg, buffer = buffer.split(b'\n', 1)
                            try:
                                traffic_data = json.loads(msg.decode())
                                self.update_vehicles(traffic_data.get("queues", {}))

                                # Get light states from shared memory
                                shared_data = self.fetch_shared_memory_data()
                                lights_state = shared_data.get("lights", {})
                                self.process_message_queue()
                                
                                # Render the display
                                screen.fill((0, 0, 0))  # Clear screen
                                screen.blit(BACKGROUND_IMG, (0, 0))  # Draw intersection
                                self.draw_traffic_lights(lights_state)
                                self.draw_vehicles()
                                pygame.display.flip()
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.error(f"Connection error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    shutdown_flag = threading.Event()
    shared_mem_name = "traffic_shared_mem"  # Example shared memory name
    message_queue = Queue()
    display = TrafficDisplay(shutdown_flag, shared_mem_name, message_queue)
    
    pygame_thread = threading.Thread(target=display.run)
    pygame_thread.start()
    
    # Handle Quit Event
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shutdown_flag.set()
                running = False
    
    pygame.quit()
    pygame_thread.join()