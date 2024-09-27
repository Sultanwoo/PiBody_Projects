from tester.tester import Tester
from machine import Pin, PWM
from utime import sleep
from root_tools import display, color565

class MotionTester(Tester):
    name = "Motion Detector"
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins

    def start(self):    
        super().start()
        return True

    def test(self):
        for pin in self.pins:
            self.detector = Pin(pin, Pin.IN)
            if self.detector.value() == 1:
                display.display_text("Motion is detected", 50, display.height - 70)
                display.fill_circle(display.width // 2, display.height  - 100, 10,  color565(0, 255, 0))
                return
        display.display_text("No motion detected", 50, display.height - 50)
        display.fill_circle(display.width // 2, display.height  - 80, 10,  color565(0, 0, 0))

    def finish(self):
        super().finish()
        
