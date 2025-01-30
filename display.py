# display.py
import socket
import json
import time
import logging
from enum import Enum
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
logger = logging.getLogger("display")

class LightColor(Enum):
    GREEN = Fore.GREEN + "🟢" + Style.RESET_ALL
    RED = Fore.RED + "🔴" + Style.RESET_ALL

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