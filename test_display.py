#!/usr/bin/env python3
import pygame
import sys
import time
import random

# This version of the GUI does not follow any of the rules (lights, turns, ...)
# It's only for testing what the GUI looks like and the animations

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crossroads Simulation Display")

clock = pygame.time.Clock()

# Define Colors
BLACK     = (0, 0, 0)
WHITE     = (255, 255, 255)
RED       = (220, 20, 60)
GREEN     = (50, 205, 50)
YELLOW    = (255, 215, 0)
GRAY      = (169, 169, 169)
DARK_GRAY = (40, 40, 40)

# Road and intersection parameters
ROAD_WIDTH = 120
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# Simulation parameters for lights:
# We'll cycle the NS and EW lights every 10 seconds.
light_cycle_duration = 10  # seconds
light_timer = 0

# Define simulation state
state = {
    "lights": {  # initial state: NS GREEN, EW RED
        "N": "GREEN",
        "S": "GREEN",
        "E": "RED",
        "W": "RED"
    },
    "vehicles": []  # list of vehicle dictionaries
}

# Vehicle structure:
# { "id": str, "type": "normal" or "emergency", "source": "N"/"S"/"E"/"W",
#   "destination": (opposite or turning), "pos": [x, y], "speed": int, "priority": bool }

vehicle_id_counter = 1

def create_vehicle(source, destination, priority=False):
    global vehicle_id_counter
    vid = f"veh{vehicle_id_counter:03d}"
    vehicle_id_counter += 1
    # Set initial position based on source
    if source == "N":
        pos = [CENTER_X - 20, -40]  # above the screen on vertical center lane
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
        pos = [0,0]
        speed = 0

    return {
        "id": vid,
        "type": "emergency" if priority else "normal",
        "source": source,
        "destination": destination,
        "pos": pos,
        "speed": speed,
        "priority": priority
    }

def update_vehicles():
    """Update the positions of vehicles based on their source direction."""
    for veh in state["vehicles"]:
        src = veh["source"]
        if src in ("N", "S"):
            # Vehicles move vertically along center_x; update y
            veh["pos"][1] += veh["speed"]
        elif src in ("E", "W"):
            veh["pos"][0] += veh["speed"]
    # Remove vehicles that have moved off-screen (simple check)
    state["vehicles"] = [veh for veh in state["vehicles"]
                         if -100 < veh["pos"][0] < WIDTH+100 and -100 < veh["pos"][1] < HEIGHT+100]

def draw_intersection():
    # Fill background
    screen.fill(DARK_GRAY)
    
    # Draw roads as rectangles
    # Horizontal road (E-W)
    pygame.draw.rect(screen, GRAY, (0, CENTER_Y - ROAD_WIDTH // 2, WIDTH, ROAD_WIDTH))
    # Vertical road (N-S)
    pygame.draw.rect(screen, GRAY, (CENTER_X - ROAD_WIDTH // 2, 0, ROAD_WIDTH, HEIGHT))
    
    # Draw intersection lines (optional)
    pygame.draw.line(screen, WHITE, (0, CENTER_Y - ROAD_WIDTH // 2), (WIDTH, CENTER_Y - ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, WHITE, (0, CENTER_Y + ROAD_WIDTH // 2), (WIDTH, CENTER_Y + ROAD_WIDTH // 2), 2)
    pygame.draw.line(screen, WHITE, (CENTER_X - ROAD_WIDTH // 2, 0), (CENTER_X - ROAD_WIDTH // 2, HEIGHT), 2)
    pygame.draw.line(screen, WHITE, (CENTER_X + ROAD_WIDTH // 2, 0), (CENTER_X + ROAD_WIDTH // 2, HEIGHT), 2)
    
    # Draw cardinal directions
    font = pygame.font.SysFont("Arial", 24)
    stdscr = screen
    stdscr.blit(font.render("N", True, WHITE), (CENTER_X - 10, 10))
    stdscr.blit(font.render("S", True, WHITE), (CENTER_X - 10, HEIGHT - 30))
    stdscr.blit(font.render("E", True, WHITE), (WIDTH - 30, CENTER_Y - 10))
    stdscr.blit(font.render("W", True, WHITE), (10, CENTER_Y - 10))
    
    # Draw traffic lights.
    # For N/S, use state["lights"]["N"]
    ns_light = state["lights"]["N"]
    ns_color = GREEN if ns_light == "GREEN" else RED
    # Draw a circle for N light above intersection.
    pygame.draw.circle(screen, ns_color, (CENTER_X - ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    # And S light below intersection.
    pygame.draw.circle(screen, ns_color, (CENTER_X + ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    
    # For E/W, use state["lights"]["E"]
    ew_light = state["lights"]["E"]
    ew_color = GREEN if ew_light == "GREEN" else RED
    # Draw E light: circle on right of intersection.
    pygame.draw.circle(screen, ew_color, (CENTER_X + ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    # Draw W light: circle on left of intersection.
    pygame.draw.circle(screen, ew_color, (CENTER_X - ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)

def draw_vehicles():
    """Draw each vehicle as a rectangle."""
    for veh in state["vehicles"]:
        # Differentiate by priority: emergency vehicles drawn in RED, normal in WHITE.
        color = RED if veh["priority"] else WHITE
        # Draw the vehicle as a rectangle.
        if veh["source"] in ("N", "S"):
            # For vertical vehicles, width=20, height=40.
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 20, 40)
        else:
            # For horizontal vehicles, width=40, height=20.
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 40, 20)
        pygame.draw.rect(screen, color, rect)
        # Optionally, draw the vehicle ID (first 4 chars)
        font = pygame.font.SysFont("Arial", 12)
        text_surface = font.render(veh["id"][:4], True, BLACK)
        screen.blit(text_surface, (veh["pos"][0], veh["pos"][1]))

def update_lights():
    """Cycle the lights based on time."""
    global light_timer
    current_time = time.time()
    # Cycle every 'light_cycle_duration' seconds.
    if current_time - light_timer > light_cycle_duration:
        # Toggle: if NS are GREEN, switch to RED and EW to GREEN; otherwise, vice versa.
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

def main():
    global light_timer
    light_timer = time.time()
    # For testing, create some vehicles periodically.
    # Every 3 seconds, spawn a random vehicle.
    spawn_timer = time.time()
    
    # Main loop.
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Quit if Q is pressed.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False

        # Update lights based on time.
        update_lights()

        # Spawn a new vehicle every 3 seconds.
        if time.time() - spawn_timer > 3:
            # Randomly choose a source.
            src = random.choice(["N", "S", "E", "W"])
            # For destination, simply pick a different random cardinal.
            dest = random.choice([d for d in ["N", "S", "E", "W"] if d != src])
            # Randomly decide if it is emergency (say, 20% chance).
            priority = random.random() < 0.2
            veh = create_vehicle(src, dest, priority)
            state["vehicles"].append(veh)
            spawn_timer = time.time()

        # Update vehicles positions.
        update_vehicles()

        # Draw the simulation.
        draw_intersection()
        draw_vehicles()

        # Draw simulation info (optional)
        font = pygame.font.SysFont("Arial", 18)
        info = f"Lights: N={state['lights']['N']} S={state['lights']['S']} E={state['lights']['E']} W={state['lights']['W']}"
        screen.blit(font.render(info, True, WHITE), (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
