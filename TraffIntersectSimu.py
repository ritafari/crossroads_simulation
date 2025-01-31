import random
import time
import threading
import pygame
import sys
import logging
from PIL import Image
import numpy as np
import lights



# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("display")

# Coordinates of vehicles' start
x = {'W->E':[0,0,0], 'N->S':[755,727,697], 'E->W':[1400,1400,1400], 'S->N':[602,627,657]}
y = {'W->E':[348,370,398], 'N->S':[0,0,0], 'E->W':[498,466,436], 'S->N':[800,800,800]}
vehicles = {'W->E': {0:[], 1:[], 2:[], 'crossed':0}, 'N->S': {0:[], 1:[], 2:[], 'crossed':0}, 'E->W': {0:[], 1:[], 2:[], 'crossed':0}, 'S->N': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'bike'}
directionNumbers = {0:'W->E', 1:'N->S', 2:'E->W', 3:'S->N'}

currentGreen = lights.normal_operation  # currentGreen = 0   # Indicates which signal is green currently

# Coordinates of signal image, timer, and vehicle count
signalCoords = [(530,230),(810,230),(810,570),(530,570)]

# Coordinates of stop lines
stopLines = {'W->E': 590, 'N->S': 330, 'E->W': 800, 'S->N': 535}
defaultStop = {'W->E': 580, 'N->S': 320, 'E->W': 810, 'S->N': 545}
# Gap between vehicles
stoppingGap = 15    # stopping gap
movingGap = 15   # moving gap
speeds = {'car':2.25, 'bus':1.8, 'bike':2.5}  # average speeds of vehicles

# Initialize the pygame
pygame.init()
simulation = pygame.sprite.Group()

"""
# Load the images
class LightColor(Enum):
    GREEN = Image.open("greenLight2.0.jpg") #load image file
    GREEN = GREEN.convert("RGB")    #convert image to RGB to ensure compatibility
    GREEN_array = np.array(GREEN)   #Convert image to a NumPy array
    GREEN = GREEN_array[:, :, 1]    #extract green channel from the image

    RED = Image.open("redLight2.0.jpg")
    RED = RED.convert("RGB")
    RED_array = np.array(RED)
    RED = RED_array[:, :, 1]
"""
    
# Defining Classes: 
#   1. Traffic Signal: We need to generate three traffic signals for simulation, we give following attributes to the signal: red (value of red signal), green (value of green signal), signalText: value of timer to display
#   2. Vehicle: We need to generate vehicles for simulation, we give following attributes to the vehicle: vehicleType (type of vehicle), direction (direction in text format),direction_number (represent dir, 0 for W->E for eg), x (x-coordinate of vehicle), 
#               y (y-coordinate of vehicle), speed (speed of vehicle), index (relative position of vehicle among the vehicles moving in the same direction and same lane), crossed (crossed flag of vehicle), image (image to be rendered), render (display the imag eon screen), move (control movement of the vehicle according to the traffic)


class TrafficSignal:
    def __init__(self, red, green, signalText):
        self.red = red
        self.green = green
        self.signalText = signalText

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.speed = speeds[vehicleClass]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane])-1
        path = "traffic/"+direction+"/"+vehicleClass+"jpg"
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):    # If there is at least one vehicle ahead in the same direction & lane and it has not crossed the intersection: The new vehicle's stopping position is adjusted based on the previous vehicle.
            # If moving right, the new vehicle stops behind the previous vehicle.It subtracts the width of the previous vehicle and the stopping gap.
            if(direction=='W->E'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap        
            elif(direction=='E->W'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif(direction=='N->S'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif(direction=='S->N'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        # If no vehicle is ahead, the car stops at the default stop position for that direction
        else:
            self.stop = defaultStop[direction]
            
        if(direction=='W->E'):  # After determining the stop position, we update the x or y coordinate for the next vehicle.
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp  # If moving right, the next vehicle is placed to the left by subtracting temp (width + gap).
        elif(direction=='E->W'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction=='N->S'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction=='S->N'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)    # Adds the current vehicle to the simulation.
    
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))   # Draws the vehicle at its position.
    
    def move(self):
        if(self.direction=='W->E'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):   # Checks if the vehicle crosses the stop line:
                self.crossed = 1    # If the vehicle's front (x + width) passes the stop line, it is marked as crossed = 1
            
            if(self.x+self.image.get_rect().width<=self.stop or self.crossed == 1 or currentGreen==0 and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):
                # Conditions for moving forward:
                #       If it hasn't reached the stopping point (self.x + width <= self.stop)
                #       If it has already crossed the stop line (self.crossed == 1).
                #       If the traffic light is green (currentGreen == 0), and:
                #               It is the first vehicle in the lane (self.index == 0), or there is enough gap from the vehicle ahead.
                self.x += self.speed    # If any of these conditions are met, the vehicle moves forward (self.x += self.speed).
        
        elif(self.direction=='N->S'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
            if(self.y+self.image.get_rect().height<=self.stop or self.crossed == 1 or currentGreen==1 and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):
                self.y += self.speed
        
        elif(self.direction=='E->W'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
            if(self.x>=self.stop or self.crossed == 1 or currentGreen==2 and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width+ movingGap))):                
                self.x -= self.speed    
        
        elif(self.direction=='S->N'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
            if(self.y>=self.stop or self.crossed == 1 or currentGreen==3 and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height+ movingGap))):                
                self.y -= self.speed



class TrafficDisplay:
    def __init__(self, shutdown_flag, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.running = True
        self.reconnect_delay = 1
        self.shutdown_flag = shutdown_flag
        

    def clear_screen(self):
        """Clear terminal using ANSI escape codes"""
        print("\033[H\033[J", end="")

    def draw_intersection(self, data):

        """Render the crossroads visualization"""
        lights = data.get("lights", {})
        queues = data.get("queues", {})
        current_vehicle = data.get("current_vehicle", {})

        # Build the intersection grid
        grid = [
            "                    NORTH                    ",
            f"  {LightColor[lights.get('N', 'RED')].value}  [N: {queues.get('N', 0):02d}]       ⬆        [S: {queues.get('S', 0):02d}]  {LightColor[lights.get('S', 'RED')].value}  ",
            "                    ⬆⬇                    ",
            "WEST ⬅ ⬅ ⬅ ⬅ ⬅ ⬅ ✖ ➡ ➡ ➡ ➡ ➡ ➡ EAST",
            "                    ⬇⬆                    ",
            f"  {LightColor[lights.get('W', 'RED')].value}  [W: {queues.get('W', 0):02d}]       ⬇        [E: {queues.get('E', 0):02d}]  {LightColor[lights.get('E', 'RED')].value}  ",
            "                    SOUTH                    "
        ]

        # Add current vehicle info
        if current_vehicle:
            vehicle_info = [
                "",
                " CURRENT VEHICLE:",
                f" ID: {current_vehicle.get('id', '')[0:8]}",
                f" Type: {current_vehicle.get('type', 'unknown')}",
                f" From: {current_vehicle.get('source', '?')} → To: {current_vehicle.get('destination', '?')}",
                f" Priority: {'🚨 ' if current_vehicle.get('priority', False) else ''}{current_vehicle.get('priority', False)}",
                f" Turn: {current_vehicle.get('turn', 'none')}"
            ]
            grid += vehicle_info

        self.clear_screen()
        print("\n".join(grid))

    def run(self):
        buffer = b""
        while not self.shutdown_flag.is_set():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    while not self.shutdown_flag.is_set():
                        data = s.recv(4096)
                        if not data: break
                        
                        buffer += data
                        while b'\n' in buffer:
                            msg, buffer = buffer.split(b'\n', 1)
                            try:
                                self.draw_intersection(json.loads(msg.decode()))
                            except json.JSONDecodeError:
                                continue
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    display = TrafficDisplay()
    display.run()