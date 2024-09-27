from tester.tester import Tester
from machine import Pin, PWM, time_pulse_us
from utime import sleep, sleep_us

from root_tools import *

class UltrasonicTester(Tester):
    name = "Ultrasonic Sensor"

    

    def __init__(self, pin):
            super().__init__(self.name, pin)
    
    def start(self):    
        super().start()
        init_loading_bar()
        self.echo = Pin(self.pin[0], Pin.IN)
        self.trigger = Pin(self.pin[1], Pin.OUT)
        return True

    def measure_distance(self):
        # Send a 10us pulse to trigger the measurement
        self.trigger.value(0)
        sleep_us(2)
        self.trigger.value(1)
        sleep_us(10)
        self.trigger.value(0)
        
        # Measure the duration of the echo pulse
        duration = time_pulse_us(self.echo, 1)
        
        # Calculate the distance in centimeters
        distance = (duration * 0.0343) / 2
        return distance

    def test(self):
        distance = self.measure_distance()
        print(f"Distance: {distance} cm")
        draw_loading_bar(min(distance / 30, 1))
        display_info(f"Distance: {distance :.2} cm")
        sleep(0.1)


    def finish(self):
        super().finish()