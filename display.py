#!/usr/bin/env python3
import pygame
import socket
import json
import threading
import time
import sys
import logging

# -------------------------------
# Configuration & Global Variables
# -------------------------------

HOST = '127.0.0.1'
PORT = 65432

# Global simulation state (will be updated by the socket listener thread)
sim_state = {
    "lights": {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"},
    "queues": {"N": 0, "S": 0, "E": 0, "W": 0},
    "current_vehicle": None,
    "event_logs": []
}
state_lock = threading.Lock()

# Configure logging.
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("display_pygame_gui")

# -------------------------------
# Pygame Initialization & Setup
# -------------------------------

pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crossroads Simulation GUI")
clock = pygame.time.Clock()

# Colors
BLACK      = (0, 0, 0)
WHITE      = (255, 255, 255)
RED        = (220, 20, 60)
GREEN      = (50, 205, 50)
YELLOW     = (255, 215, 0)
GRAY       = (169, 169, 169)
DARK_GRAY  = (40, 40, 40)
BLUE       = (30, 144, 255)

# Intersection parameters
ROAD_WIDTH = 120
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

# -------------------------------
# Socket Listener Thread
# -------------------------------

def socket_listener():
    global sim_state
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        sock.settimeout(1)
        logger.info(f"Connected to display server at {HOST}:{PORT}")
    except Exception as e:
        logger.error(f"Error connecting to display server: {e}")
        return

    buffer = b""
    while True:
        try:
            data = sock.recv(4096)
            if data:
                buffer += data
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Socket error: {e}")
            break

        while b'\n' in buffer:
            msg, buffer = buffer.split(b'\n', 1)
            if not msg.strip():
                continue
            try:
                new_state = json.loads(msg.decode())
                with state_lock:
                    sim_state = new_state
            except Exception as e:
                logger.error(f"Error decoding JSON: {e}")
        time.sleep(0.1)
    sock.close()

def start_socket_listener():
    listener_thread = threading.Thread(target=socket_listener, daemon=True)
    listener_thread.start()

# -------------------------------
# Drawing Functions
# -------------------------------

def draw_intersection():
    # Clear background.
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
    with state_lock:
        lights = sim_state.get("lights", {})
    # For N/S, use lights["N"].
    ns_color = GREEN if lights.get("N", "GREEN") == "GREEN" else RED
    pygame.draw.circle(screen, ns_color, (CENTER_X - ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    pygame.draw.circle(screen, ns_color, (CENTER_X + ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)
    
    # For E/W, use lights["E"].
    ew_color = GREEN if lights.get("E", "RED") == "GREEN" else RED
    pygame.draw.circle(screen, ew_color, (CENTER_X + ROAD_WIDTH, CENTER_Y - ROAD_WIDTH), 15)
    pygame.draw.circle(screen, ew_color, (CENTER_X - ROAD_WIDTH, CENTER_Y + ROAD_WIDTH), 15)

def draw_info():
    """Display textual information (lights, queue sizes, current vehicle, and events) in a corner."""
    with state_lock:
        lights = sim_state.get("lights", {})
        queues = sim_state.get("queues", {})
        current_vehicle = sim_state.get("current_vehicle")
        event_logs = sim_state.get("event_logs", [])
    
    font = pygame.font.SysFont("Arial", 18)
    info_lines = [
        f"Lights: N={lights.get('N','?')} S={lights.get('S','?')} E={lights.get('E','?')} W={lights.get('W','?')}",
        f"Queues: N={queues.get('N',0)} S={queues.get('S',0)} E={queues.get('E',0)} W={queues.get('W',0)}"
    ]
    if current_vehicle:
        info_lines.append("Current Vehicle:")
        info_lines.append(f" ID: {current_vehicle.get('id','')[:8]}")
        info_lines.append(f" Type: {current_vehicle.get('type','')}")
        info_lines.append(f" From: {current_vehicle.get('source','')} -> To: {current_vehicle.get('destination','')}")
        info_lines.append(f" Turn: {current_vehicle.get('turn','')}, Priority: {current_vehicle.get('priority',False)}")
    else:
        info_lines.append("No current vehicle.")
    info_lines.append("Recent Events:")
    if event_logs:
        for ev in event_logs:
            info_lines.append(f" - {ev.get('msg','')}")
    else:
        info_lines.append(" None")
    
    # Draw the text in the top-left corner.
    y = 10
    for line in info_lines:
        text_surf = font.render(line, True, WHITE)
        screen.blit(text_surf, (10, y))
        y += 20

def draw_simulation():
    draw_intersection()
    draw_info()
    # (Optionally, if your simulation state includes vehicle positions, draw them here)
    # If your state includes vehicles (as a list), you can call a draw_vehicles() function.
    with state_lock:
        vehicles = sim_state.get("vehicles", [])
    for veh in vehicles:
        # For demonstration, draw vehicles as small rectangles.
        color = RED if veh.get("priority", False) else WHITE
        if veh["source"] in ("N", "S"):
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 20, 40)
        else:
            rect = pygame.Rect(veh["pos"][0], veh["pos"][1], 40, 20)
        pygame.draw.rect(screen, color, rect)
        font = pygame.font.SysFont("Arial", 12)
        text = font.render(veh["id"][:4], True, BLACK)
        screen.blit(text, (veh["pos"][0], veh["pos"][1]))

# -------------------------------
# Main Loop
# -------------------------------

def main():
    # Start the socket listener thread.
    start_socket_listener()
    
    running = True
    while running:
        # Handle Pygame events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Optionally, allow quitting via a key.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
        
        # Clear the screen.
        screen.fill(BLACK)
        # Draw the simulation state.
        draw_simulation()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
