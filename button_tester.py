from tester.tester import Tester
from machine import Pin, PWM
from utime import sleep
from root_tools import display, color565

class ButtonTester(Tester):
    name = "Push Button"
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
        
    def start(self):    
        super().start()
        return True
    
    def test(self):
        for pin in self.pins: 
            self.touch = Pin(pin, Pin.IN)
            if self.touch.value() == 1:
                display.fill_circle(display.width // 2, display.height  - 80, 10,  color565(0, 255, 0))
                return
        display.fill_circle(display.width // 2, display.height  - 80, 10,  color565(0, 0, 0))

    def finish(self):
        super().finish()
        
