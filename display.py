import socket
import json
import time
import sys

HOST = '127.0.0.1'
PORT = 65432

def print_state(state):
    lights = state.get("lights", {})
    queues = state.get("queues", {})
    current_vehicle = state.get("current_vehicle", None)
    event_logs = state.get("event_logs", [])
    
    report = []
    report.append("==== Current Simulation State ====")
    report.append(f"Traffic Lights: N={lights.get('N', '?')}, S={lights.get('S', '?')}, E={lights.get('E', '?')}, W={lights.get('W', '?')}")
    report.append(f"Vehicle Queues: N={queues.get('N', 0)}, S={queues.get('S', 0)}, E={queues.get('E', 0)}, W={queues.get('W', 0)}")
    
    if current_vehicle:
        report.append("Current Vehicle:")
        report.append(f"  ID: {current_vehicle.get('id','')[:8]}")
        report.append(f"  Type: {current_vehicle.get('type','')}")
        report.append(f"  From: {current_vehicle.get('source','')} -> To: {current_vehicle.get('destination','')}")
        report.append(f"  Turn: {current_vehicle.get('turn','')}, Priority: {current_vehicle.get('priority', False)}")
    else:
        report.append("No current vehicle processing.")
    
    report.append("Recent Events:")
    if event_logs:
        for ev in event_logs:
            report.append(f"  {ev.get('msg','')}")
    else:
        report.append("  No recent events.")
    report.append("=" * 40)
    
    # Clear the console
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()
    print("\n".join(report))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        sock.settimeout(1)
        print(f"Connected to display server at {HOST}:{PORT}")
    except Exception as e:
        print(f"Error connecting to display server: {e}")
        return
    
    buffer = b""
    while True:
        try:
            data = sock.recv(4096)
            if data:
                buffer += data
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            print("Keyboard interrupt received. Exiting display.")
            break
        
        while b'\n' in buffer:
            msg, buffer = buffer.split(b'\n', 1)
            if not msg.strip():
                continue
            try:
                state = json.loads(msg.decode())
                print_state(state)
            except Exception as e:
                print(f"Error decoding JSON: {e}")
        time.sleep(1)
    sock.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Display interrupted. Exiting.")
