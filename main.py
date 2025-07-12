import pyspacemouse
import time
import socket
import json
from collections import namedtuple

SERVER_IP = '10.0.0.105'
SERVER_PORT = 5005
DEADZONE = 0.15

class SpaceMouseController:
    def __init__(self, deadzone_threshold=0.1, calibration_samples=50):
        self.deadzone_threshold = deadzone_threshold
        self.calibration_samples = calibration_samples
        self.calibration_data = None
        self.is_calibrated = False

    def calibrate(self):
        print("Calibrating SpaceMouse... Please don't touch the device.")
        samples = []

        while len(samples) < self.calibration_samples:
            try:
                state = pyspacemouse.read()
                if state:
                    samples.append([state.x, state.y, state.z,
                                    state.roll, state.pitch, state.yaw])
                time.sleep(0.05)
            except Exception as e:
                print(f"Error reading device: {e}")
                continue

        if not samples:
            print("Calibration failed: no data received.")
            return

        self.calibration_data = [sum(axis) / len(axis) for axis in zip(*samples)]
        self.is_calibrated = True
        print("Calibration complete. Offset values:", self.calibration_data)

    def get_calibrated_state(self):
        if not self.is_calibrated:
            self.calibrate()
            if not self.is_calibrated:
                return None

        try:
            raw_state = pyspacemouse.read()
        except Exception as e:
            print(f"Error reading device: {e}")
            return None

        if not raw_state:
            return None

        calibrated_values = {
            'x': raw_state.x - self.calibration_data[0],
            'y': raw_state.y - self.calibration_data[1],
            'z': raw_state.z - self.calibration_data[2],
            'roll': raw_state.roll - self.calibration_data[3],
            'pitch': raw_state.pitch - self.calibration_data[4],
            'yaw': raw_state.yaw - self.calibration_data[5],
            'buttons': raw_state.buttons
        }

        for key in ['x', 'y', 'z', 'roll', 'pitch', 'yaw']:
            calibrated_values[key] = self.apply_deadzone(calibrated_values[key])

        return calibrated_values
    
    def apply_deadzone(self, value):
        return 0.0 if abs(value) < self.deadzone_threshold else value
    
    def normalize_data(self, state):
        """Normalize the state data to a range of -1 to 1"""
        normalized = {}
        for key in ['x', 'y', 'z', 'roll', 'pitch', 'yaw']:
            if abs(state[key]) > 0.0001:
                if state[key] > 0:
                    normalized[key] = (state[key] - self.deadzone_threshold) / (1.0 - self.deadzone_threshold)
                else:
                    normalized[key] = (state[key] + self.deadzone_threshold) / (1.0 - self.deadzone_threshold)
            else:
                normalized[key] = 0.0
        normalized['buttons'] = state['buttons']
        return normalized


def button_callback(buttons):
    print(f"Buttons pressed: {buttons}")

def is_zero_state(state):
    """Check if all axes are zero and no buttons are pressed"""
    for key in ['x', 'y', 'z', 'roll', 'pitch', 'yaw']:
        if abs(state[key]) > 0.0001:  # small epsilon to account for floating point
            return False
    return not any(state['buttons'])

def main():
    controller = SpaceMouseController(deadzone_threshold=DEADZONE)

    success = pyspacemouse.open(
        dof_callback=None,
        button_callback=button_callback
    )

    if not success:
        print("Failed to open SpaceMouse connection")
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((SERVER_IP, SERVER_PORT))
            print("Connected to TCP server at", SERVER_IP, SERVER_PORT)
            print("Move the device or press buttons (Ctrl+C to quit)")

            zero_count = 0
            last_non_zero_state = None
            is_sleeping = False

            while True:
                state = controller.get_calibrated_state()
                state = controller.normalize_data(state)
                if state:
                    if is_zero_state(state):
                        zero_count += 1
                        if zero_count >= 10 and not is_sleeping:
                            print("Detected 10 zero states - entering sleep mode")
                            is_sleeping = True
                    else:
                        zero_count = 0
                        last_non_zero_state = state
                        if is_sleeping:
                            print("Detected movement - waking up")
                            is_sleeping = False

                    if not is_sleeping:
                        # Zamiana danych na JSON i wysłanie
                        message = json.dumps(state).encode('utf-8')
                        sock.sendall(message + b'\n')  # newline jako separator ramek
                    elif last_non_zero_state is not None:
                        # Sprawdź, czy stan się zmienił (np. przycisk został naciśnięty)
                        current_state = controller.get_calibrated_state()
                        if current_state and (current_state['buttons'] != last_non_zero_state['buttons'] or 
                                            not is_zero_state(current_state)):
                            zero_count = 0
                            is_sleeping = False
                            print("State changed - waking up")
                            message = json.dumps(current_state).encode('utf-8')
                            sock.sendall(message + b'\n')

                time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nExiting...")

    except ConnectionRefusedError:
        print("Unable to connect to TCP server. Is it running?")

    finally:
        pyspacemouse.close()


if __name__ == "__main__":
    main()