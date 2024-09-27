from tester.tester import Tester
from machine import Pin, PWM, time_pulse_us
from utime import sleep, sleep_us
from root_tools import *
from libs.rotary_irq_rp2 import RotaryIRQ

class EncoderTester(Tester):
    name = "Encoder"
    counter = 0
    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
    
    def start(self):    
        super().start()
        init_loading_bar()
        self.encoder0 = RotaryIRQ(self.pins[0], self.pins[1], min_val=-15, max_val=15, incr=1, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP)
        self.encoder1 = RotaryIRQ(self.pins[2], self.pins[3], min_val=-15, max_val=15, incr=1, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP)
        self.encoder2 = RotaryIRQ(self.pins[4], self.pins[5], min_val=-15, max_val=15, incr=1, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP)
        self.encoder3 = RotaryIRQ(self.pins[6], self.pins[7], min_val=-15, max_val=15, incr=1, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP)
        return True

    def test(self):
        self.counter = self.encoder0.value() + self.encoder1.value() + self.encoder2.value() + self.encoder3.value() + 60
        self.counter = (self.counter % 31) - 15
        value = max(min((self.counter + 15) / 30, 1), 0)
        draw_loading_bar(value)
        display_info(f"Counter: {self.counter}")
        # Optional debounce delay

# Set up the encoder pins

# Initialize counter and previous state variable
