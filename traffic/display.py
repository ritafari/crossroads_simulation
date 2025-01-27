# Visualization of the simulation

"""
def display(shared_memory):
    #Render the intersection state to the operator.
    while True:
        state = shared_memory.get_state()
        render(state)  # Render the state visually
        time.sleep(0.5)
"""
"""
import socket
import json
def display_client(host="127.0.0.1", port=65432):
    #Display client connects to the coordinator server to receive real-time updates
    #and visualizes the data.
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        while True:
            data = client_socket.recv(1024)  # Receive data (up to 1024 bytes)
            if not data:
                print("No data received. Closing connection...")
                break
            update_message = json.loads(data.decode("utf-8"))
            print(f"Received update: {update_message}")
    except Exception as e:
        print(f"Error in display_client: {e}")
    finally:
        client_socket.close()
"""
import sys
import socket
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsEllipseItem
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtCore import QTimer



class CrossroadsDisplay(QMainWindow):
    def display_client(self, host="127.0.0.1", port=65432):
        super().__init__()
        self.setWindowTitle("Crossroads Traffic Simulation")
        self.setGeometry(100, 100, 600, 600)

        # PyQt Graphics Scene and View
        self.scene = QGraphicsScene(0, 0, 600, 600)
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        # Draw roads
        self.draw_roads()

        # Traffic lights and vehicles
        self.traffic_lights = {}
        self.vehicles = {}

        # Draw initial traffic lights
        self.init_traffic_lights()

        # Socket for receiving updates
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

        # Timer for regular updates (GUI responsiveness)
        self.timer = QTimer()
        self.timer.timeout.connect(self.receive_updates)
        self.timer.start(100)  # Check for updates every 100ms

        self.connect_to_server()

    def draw_roads(self):
        """Draw the roads on the crossroads."""
        # Vertical road
        self.scene.addRect(250, 0, 100, 600, brush=QBrush(QColor("gray")))
        # Horizontal road
        self.scene.addRect(0, 250, 600, 100, brush=QBrush(QColor("gray")))

    def init_traffic_lights(self):
        """Initialize traffic lights at the corners of the intersection."""
        self.traffic_lights["N"] = self.create_light(275, 150, "red")
        self.traffic_lights["S"] = self.create_light(275, 450, "red")
        self.traffic_lights["W"] = self.create_light(150, 275, "green")
        self.traffic_lights["E"] = self.create_light(450, 275, "green")

    def create_light(self, x, y, color):
        """Create a traffic light as a circle with a given color."""
        light = QGraphicsEllipseItem(x, y, 50, 50)
        light.setBrush(QBrush(QColor(color)))
        self.scene.addItem(light)
        return light

    def update_traffic_lights(self, lights_state):
        """Update the color of traffic lights based on the state."""
        for direction, state in lights_state.items():
            color = "green" if state == "green" else "red"
            self.traffic_lights[direction].setBrush(QBrush(QColor(color)))

    def add_vehicle(self, vehicle_id, x, y, vehicle_type):
        """Add a vehicle to the scene."""
        color = "blue" if vehicle_type == "normal" else "orange"
        vehicle = QGraphicsRectItem(x, y, 20, 20)
        vehicle.setBrush(QBrush(QColor(color)))
        self.scene.addItem(vehicle)
        self.vehicles[vehicle_id] = vehicle

    def update_vehicle_position(self, vehicle_id, x, y):
        """Update the position of a vehicle."""
        if vehicle_id in self.vehicles:
            self.vehicles[vehicle_id].setRect(x, y, 20, 20)

    def remove_vehicle(self, vehicle_id):
        """Remove a vehicle from the scene."""
        if vehicle_id in self.vehicles:
            self.scene.removeItem(self.vehicles[vehicle_id])
            del self.vehicles[vehicle_id]

    def connect_to_server(self):
        """Connect to the coordinator server."""
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.timer.stop()

    def receive_updates(self):
        """Receive updates from the server and process them."""
        try:
            self.socket.settimeout(0.1)  # Non-blocking
            data = self.socket.recv(1024)
            if not data:
                print("Server closed connection.")
                self.timer.stop()
                self.socket.close()
                return

            # Process the received update
            update_message = json.loads(data.decode("utf-8"))
            self.handle_update(update_message)

        except socket.timeout:
            pass  # No data received within timeout
        except Exception as e:
            print(f"Error receiving updates: {e}")

    def handle_update(self, message):
        """Handle updates from the server."""
        if message["type"] == "traffic_light_update":
            self.update_traffic_lights(message["state"])
        elif message["type"] == "vehicle_update":
            vehicle_id = message["vehicle_id"]
            if message["action"] == "add":
                self.add_vehicle(vehicle_id, message["x"], message["y"], message["vehicle_type"])
            elif message["action"] == "update":
                self.update_vehicle_position(vehicle_id, message["x"], message["y"])
            elif message["action"] == "remove":
                self.remove_vehicle(vehicle_id)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    display = CrossroadsDisplay(host="127.0.0.1", port=65432)
    display.show()
    sys.exit(app.exec_())
