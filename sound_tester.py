from tester.tester import Tester
from machine import Pin, ADC
from utime import sleep

from root_tools import *

class SoundTester(Tester):
    name = "Microphone"
    last_digital = 0

    def show_circle(self, value):
        if value == self.last_digital:
            return
        display.fill_circle(display.width // 2, display.height  - 100, 10,  color565(0, value * 255, 0))
        self.last_digital = value

    def __init__(self, pin):
        super().__init__(self.name, pin)
        self.pin = pin

    def start(self):
        super().start()
        self.analog = ADC(Pin(self.pin[1]))
        self.digital = Pin(self.pin[0])
        init_loading_bar()
        return True

    def test(self):
        sound_analog = self.analog.read_u16()
        sound_digital = self.digital.value()
        draw_loading_bar(sound_analog / 65535)
        self.show_circle(sound_digital)
        sleep_ms(1)

    def finish(self):
        super().finish()
