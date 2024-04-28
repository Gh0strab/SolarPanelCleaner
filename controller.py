import threading
import time
import board
import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit

class cleaner_logic:
    def __init__(self, gui_instance):
        self.gui_instance = gui_instance
        self.kit = MotorKit(i2c=board.I2C())
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.setup_gpio()
        self.task_running = False
        self.direction = 1.0

    def setup_gpio(self):
        self.limit_switch_1_pin = 16
        self.limit_switch_2_pin = 25
        self.shutoff_valve_relay_pin = 18
        GPIO.setup(self.limit_switch_1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.limit_switch_2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.shutoff_valve_relay_pin, GPIO.OUT)

    def run_motors(self):
        throttle_value = 0.5  # Initial throttle value
        while self.task_running:
            self.kit.motor1.throttle = throttle_value * self.direction
            self.kit.motor2.throttle = throttle_value * self.direction

    def check_limit_switch(self):
        return GPIO.input(self.limit_switch_1_pin) or GPIO.input(self.limit_switch_2_pin)

    def water_system_state(self, state):
        GPIO.output(self.shutoff_valve_relay_pin, GPIO.HIGH if state == "on" else GPIO.LOW)
        self.gui_instance.after(0, self.gui_instance.debug_window,f"Water System {'on' if state == 'on' else 'off'}\n")

    def reset_system(self):
        self.stop_task()
        self.water_system_state('off')
        self.kit.motor1.throttle = 0.0
        self.kit.motor2.throttle = 0.0
        self.direction = 1.0

    def perform_task(self):
        self.task_running = True
        self.water_system_state('on')

        motor_thread = threading.Thread(target=self.run_motors)
        motor_thread.start()

        while self.task_running:
            if self.check_limit_switch():
                if GPIO.input(self.limit_switch_1_pin) == GPIO.HIGH:
                    self.gui_instance.debug_window("Limit Switch 1 Hit;\n" + "Homing System\n")
                    self.direction = 1.0
                    while GPIO.input(self.limit_switch_1_pin) == GPIO.HIGH:
                        print("Limit switch 1 still pressed")
                        time.sleep(0.1)  # Add a small delay to avoid busy waiting
                    print("Limit switch 1 released")
                    break
                elif GPIO.input(self.limit_switch_2_pin) == GPIO.HIGH:
                    self.gui_instance.debug_window("Limit Switch 2 Hit;\n" + "Reversing Direction\n")
                    self.direction = -1.0
                    self.water_system_state('off')
                time.sleep(.05)

        # Resets system values to be ready to go again
        self.reset_system()

    def stop_task(self):
        self.task_running = False

    def home(self):
        self.task_running = True
        self.gui_instance.debug_window("Homing System")
        self.direction = -1.0
        motor_thread = threading.Thread(target=self.run_motors)
        motor_thread.start()
        while self.task_running:
            if self.check_limit_switch():
                if self.check_limit_switch() == "Limit switch 1":
                    self.gui_instance.after(0, self.gui_instance.debug_window,"Limit Switch 1 Hit;\n" + "Homing System\n")
                    self.direction = 1.0
                    while GPIO.input(self.limit_switch_1_pin) == GPIO.HIGH:
                        print("Limit switch 1 still pressed")
                        time.sleep(0.1)  # Add a small delay to avoid busy waiting
                    print("Limit switch 1 released")
                    break
        self.gui_instance.stop_task()  # Stop task when limit switch is hit
        self.task_running = False
        self.reset_system()

    def __del__(self):
        GPIO.cleanup()
