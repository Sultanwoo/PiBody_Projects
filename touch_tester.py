from tester.tester import Tester
from machine import Pin, PWM
from utime import sleep
from root_tools import display, color565

class TouchTester(Tester):
    name = "Touch, Push Button"
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins

    def start(self):
        super().start()
        return True

    def test(self):
        i = 0
        for pin in self.pins:
            self.touch = Pin(pin, Pin.IN)
            p = i + 1
            n = 1
            if i > 1:
                p += 1
            if i > 3:
                n = 0
                p += 2
            if i > 5:
                p += 1
            if self.touch.value() == 1:
                display.fill_circle(display.width // 7 * (p%7) + 25, display.height  - 120 - (30*n), 10,  color565(0, 255, 0))
            else:
                display.fill_circle(display.width // 7 * (p%7) + 25, display.height  - 120 - (30*n), 10,  color565(0, 0, 0))
            i += 1
        return

    def finish(self):
        super().finish()

