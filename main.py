import pyspacemouse
import time
from collections import namedtuple

class SpaceMouseController:
    def __init__(self, deadzone_threshold=0.1, calibration_samples=50):
        self.deadzone_threshold = deadzone_threshold
        self.calibration_samples = calibration_samples
        self.calibration_data = None
        self.is_calibrated = False

    def apply_deadzone(self, value):
        return 0.0 if abs(value) < self.deadzone_threshold else value

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

        # Tworzymy słownik z danymi po kalibracji
        calibrated_values = {
            'x': raw_state.x - self.calibration_data[0],
            'y': raw_state.y - self.calibration_data[1],
            'z': raw_state.z - self.calibration_data[2],
            'roll': raw_state.roll - self.calibration_data[3],
            'pitch': raw_state.pitch - self.calibration_data[4],
            'yaw': raw_state.yaw - self.calibration_data[5],
            'buttons': raw_state.buttons
        }

        # Zastosuj deadzone
        for key in ['x', 'y', 'z', 'roll', 'pitch', 'yaw']:
            calibrated_values[key] = self.apply_deadzone(calibrated_values[key])

        # Zwracamy po prostu słownik jako reprezentację stanu
        return calibrated_values


    def print_state(self, state):
        if state:
            print(f"X: {state['x']:.3f}, Y: {state['y']:.3f}, Z: {state['z']:.3f}, "
                f"Roll: {state['roll']:.3f}, Pitch: {state['pitch']:.3f}, Yaw: {state['yaw']:.3f}, "
                f"Buttons: {state['buttons']}")


def button_callback(buttons):
    print(f"Buttons pressed: {buttons}")

def main():
    controller = SpaceMouseController(deadzone_threshold=0.05)

    # Do not use callback for position – we handle it manually with calibration
    success = pyspacemouse.open(
        dof_callback=None,
        button_callback=button_callback
    )

    if not success:
        print("Failed to open SpaceMouse connection")
        return

    try:
        print("SpaceMouse connected. Move the device or press buttons (Ctrl+C to quit)")
        while True:
            state = controller.get_calibrated_state()
            if state:
                controller.print_state(state)
            time.sleep(0.02)  # 50 Hz refresh rate

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        pyspacemouse.close()

if __name__ == "__main__":
    main()

