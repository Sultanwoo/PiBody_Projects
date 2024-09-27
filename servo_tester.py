from tester.tester import Tester
from machine import Pin, PWM
from utime import sleep

from root_tools import right_btn, display
class ServoTester(Tester):
    name = "Servo"
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
        
    def start(self):
        super().start()
        return True
    
    def set_angle(self, angle):
        # Convert angle to duty cycle (16-bit integer)
        duty = int((angle / 180 * 2 + 0.5) * 65535 / 20)
        self.servo.duty_u16(duty)

    def test(self):
        for pin in self.pins:
            self.servo = PWM(Pin(pin))
            self.servo.freq(50)
            self.set_angle(right_btn.value() * 180)

    def finish(self):
        super().finish()
        # self.servo.deinit()
        


  