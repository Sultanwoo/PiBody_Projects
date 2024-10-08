from tester.tester import Tester
from machine import Pin

from root_tools import *
class LedTester(Tester):
    name = "LED"
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins

    def start(self):
        super().start()
        display.display_text("Press any button to turn LED on", 30, 100)
        return True

    def test(self):
        for pin in self.pins:
            self.led = Pin(pin, Pin.OUT)
            temp = 0
            if ctrl_button.value() or left_button.value() or down_button.value() or up_button.value():
                temp = 1
            self.led.value(temp)

    def finish(self):
        super().finish()
        for pin in self.pins:
            self.led = Pin(pin, Pin.OUT)
            self.led.value(0)
        