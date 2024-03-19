import time
import threading
import board
import RPi.GPIO as GPIO
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

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
        self.led_relay_pin = 18
        self.shutoff_valve_relay_pin = 17
        GPIO.setup(self.limit_switch_1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.limit_switch_2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led_relay_pin, GPIO.OUT)
        GPIO.setup(self.shutoff_valve_relay_pin, GPIO.OUT)

    def run_motors(self):
        throttle_value = 0.5  # Initial throttle value
        while self.task_running:
            self.kit.motor1.throttle = throttle_value * self.direction
            self.kit.motor2.throttle = throttle_value * self.direction
    def check_limit_switch(self):
        return GPIO.input(self.limit_switch_1_pin) or GPIO.input(self.limit_switch_2_pin)

    def led_state(self, state):
        GPIO.output(self.led_relay_pin, GPIO.HIGH if state == "on" else GPIO.LOW)

    def water_system_state(self, state):
        GPIO.output(self.shutoff_valve_relay_pin, GPIO.HIGH if state == "on" else GPIO.LOW)
        self.gui_instance.debug_window(f"Water System {'on' if state == 'on' else 'off'}\n")

    def perform_task(self):
        start_time = time.time()
        self.task_running = True
        self.led_state('on')
        self.water_system_state('on')

        motor_thread = threading.Thread(target=self.run_motors)
        motor_thread.start()

        while self.task_running:  # Check flag to see if task should continue
            if time.time() - start_time >= 1:
                if self.check_limit_switch():
                    self.gui_instance.debug_window("Limit Switch Hit;\n Stopping Program")
                    self.gui_instance.stop_task()  # Stop task when limit switch is hit
                    self.task_running = False
                    break
            elif self.check_limit_switch():
                self.gui_instance.debug_window("Limit Switch Hit;\n Reversing Direction")
                self.direction = -1.0
            time.sleep(0.1)

        self.led_state('off')
        self.water_system_state('off')
        self.kit.motor1.throttle = 0.0
        self.kit.motor2.throttle = 0.0
        self.direction = 1.0
    def stop_task(self):
        self.task_running = False

    def __del__(self):
        GPIO.cleanup()
