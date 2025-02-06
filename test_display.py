#!/usr/bin/env python3
import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crossroads Simulation Dashboard")

clock = pygame.time.Clock()

# Define Colors
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
RED        = (220, 20, 60)
GREEN      = (50, 205, 50)
YELLOW     = (255, 215, 0)
GRAY       = (169, 169, 169)
DARK_GRAY  = (40, 40, 40)

# Road and intersection parameters
ROAD_WIDTH = 120
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# Simulation state (dummy state for display demo)
state = {
    "lights": {  # initial state: NS GREEN, EW RED
        "N": "GREEN",
        "S": "GREEN",
        "E": "RED",
        "W": "RED"
    },
    "vehicles": []  # list of vehicles
}

# We'll cycle the lights every 10 seconds.
light_cycle_duration = 10
light_timer = 0

# Vehicle counter for unique IDs.
vehicle_id_counter = 1

def create_vehicle(source, destination, turn="straight", priority=False):
    global vehicle_id_counter
    vid = f"veh{vehicle_id_counter:03d}"
    vehicle_id_counter += 1

    # Set initial position based on source.
    if source == "N":
        pos = [CENTER_X - 20, -40]
        speed = random.randint(2, 4)
    elif source == "S":
        pos = [CENTER_X + 20, HEIGHT + 40]
        speed = -random.randint(2, 4)
    elif source == "E":
        pos = [WIDTH + 40, CENTER_Y - 20]
        speed = -random.randint(2, 4)
    elif source == "W":
        pos = [-40, CENTER_Y + 20]
        speed = random.randint(2, 4)
    else:
        pos = [0, 0]
        speed = 0

    return {
        "id": vid,
        "type": "emergency" if priority else "normal",
        "source": source,
        "destination": destination,
        "pos": pos,
        "speed": speed,
        "turn": turn,
        "priority": priority
    }

def update_vehicles():
    """Update the positions of vehicles based on their source direction.
    
    Vehicles will only move if their corresponding light is GREEN.
    For N and S, check state["lights"]["N"] (assumed shared); for E and W, check state["lights"]["E"].
    """
    new_vehicle_list = []
    for veh in state["vehicles"]:
        src = veh["source"]
        # Check light state:
        if src in ("N", "S"):
            if state["lights"]["N"] != "GREEN":
                new_vehicle_list.append(veh)
                continue  # vehicle stops if the NS light is RED.
            veh["pos"][1] += veh["speed"]
        elif src in ("E", "W"):
            if state["lights"]["E"] != "GREEN":
                new_vehicle_list.append(veh)
                continue  # vehicle stops if the EW light is RED.
            veh["pos"][0] += veh["speed"]
        new_vehicle_list.append(veh)
    state["vehicles"] = [veh for veh in new_vehicle_list
                         if -100 < veh["pos"][0] < WIDTH+100 and -100 < veh["pos"][1] < HEIGHT+100]

def draw_intersection():
    """Draw roads, intersection, lights, and cardinal directions."""
    screen.fill(DARK_GRAY)
    
    # Draw roads.
    pygame.draw.rect(screen, GRAY, (0, CENTER_Y - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH))
    pygame.draw.rect(screen, GRAY, (CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT))
    
    # Draw intersection lines.
    pygame.draw.line(screen, WHITE, (0, CENTER_Y - ROAD_WIDTH // 2), (WIDTH, CENTER_Y - ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, WHITE, (0, CENTER_Y + ROAD_WIDTH // 2), (WIDTH, CENTER_Y + ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, WHITE, (CENTER_X - ROAD_WIDTH // 2, 0), (CENTER_X - ROAD_WIDTH // 2, HEIGHT), 2)
    pygame.draw.line(screen, WHITE, (CENTER_X + ROAD_WIDTH // 2, 0), (CENTER_X + ROAD_WIDTH // 2, HEIGHT), 2)
    
    # Draw cardinal direction labels.
    font = pygame.font.SysFont("Arial", 28)
    screen.blit(font.render("N", True, WHITE), (CENTER_X - 10, 10))
    screen.blit(font.render("S", True, WHITE), (CENTER_X - 10, HEIGHT - 40))
    screen.blit(font.render("E", True, WHITE), (WIDTH - 40, CENTER_Y - 10))
    screen.blit(font.render("W", True, WHITE), (10, CENTER_Y - 10))
    
    # Draw traffic lights.
    # Use state["lights"]["N"] for NS.
    ns_light = state["lights"]["N"]
    ns_color = GREEN if ns_light == "GREEN" else RED
    pygame.draw.circle(screen, ns_color, (CENTER_X - ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    pygame.draw.circle(screen, ns_color, (CENTER_X + ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    
    # Use state["lights"]["E"] for EW.
    ew_light = state["lights"]["E"]
    ew_color = GREEN if ew_light == "GREEN" else RED
    pygame.draw.circle(screen, ew_color, (CENTER_X + ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    pygame.draw.circle(screen, ew_color, (CENTER_X - ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    
    # Optionally, draw a border around the intersection.
    pygame.draw.rect(screen, WHITE, (CENTER_X - ROAD_WIDTH // 2, CENTER_Y - ROAD_WIDTH // 2, ROAD_WIDTH, ROAD_WIDTH), 2)

def draw_vehicles():
    """Draw each vehicle as a rectangle with an ID label."""
    for veh in state["vehicles"]:
        # Distinguish emergency vehicles by color.
        color = RED if veh["priority"] else WHITE
        if veh["source"] in ("N", "S"):
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 20, 40)
        else:
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 40, 20)
        pygame.draw.rect(screen, color, rect)
        # Draw the vehicle ID (first 4 characters) on the vehicle.
        font = pygame.font.SysFont("Arial", 12)
        text_surface = font.render(veh["id"][:4], True, BLACK)
        screen.blit(text_surface, (veh["pos"][0], veh["pos"][1]))

def update_lights():
    """Cycle the traffic lights based on time.
    
    For this demonstration, NS and EW lights swap every light_cycle_duration seconds.
    """
    global light_timer
    current_time = time.time()
    if current_time - light_timer > light_cycle_duration:
        if state["lights"]["N"] == "GREEN":
            state["lights"]["N"] = "RED"
            state["lights"]["S"] = "RED"
            state["lights"]["E"] = "GREEN"
            state["lights"]["W"] = "GREEN"
        else:
            state["lights"]["N"] = "GREEN"
            state["lights"]["S"] = "GREEN"
            state["lights"]["E"] = "RED"
            state["lights"]["W"] = "RED"
        light_timer = current_time

def update_simulation():
    """Update the simulation state: traffic lights and vehicles."""
    update_lights()
    update_vehicles()

def draw_info():
    """Draw simulation information in the top-left corner."""
    font = pygame.font.SysFont("Arial", 18)
    info_text = f"Lights: N={state['lights']['N']}  S={state['lights']['S']}  E={state['lights']['E']}  W={state['lights']['W']}"
    screen.blit(font.render(info_text, True, WHITE), (10, 10))
    
    # You could also display queue lengths or other state details here.
    
def main():
    global light_timer
    light_timer = time.time()
    # Spawn some vehicles for demonstration.
    state["vehicles"].append(create_vehicle("N", "E", turn="straight"))
    state["vehicles"].append(create_vehicle("S", "W", turn="left"))
    state["vehicles"].append(create_vehicle("E", "W", turn="right", priority=True))
    state["vehicles"].append(create_vehicle("W", "S", turn="left"))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
        
        update_simulation()
        draw_intersection()
        draw_vehicles()
        draw_info()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
