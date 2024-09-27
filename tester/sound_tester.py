from tester.tester import Tester
from machine import Pin, ADC
from utime import sleep

from root_tools import *

class SoundTester(Tester):
    name = "Microphone"

    def __init__(self, pin):
        super().__init__(self.name, pin)
        self.pin = pin

    def start(self):
        super().start()
        self.analog = ADC(Pin(self.pin[0]))
        init_loading_bar()


        return True

    def test(self):
        sound_analog = self.analog.read_u16()
        draw_loading_bar(sound_analog / 65535)
        sleep_ms(1)


    def finish(self):
        super().finish()
