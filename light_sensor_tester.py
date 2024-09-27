from tester.tester import Tester
from machine import Pin, ADC
from utime import sleep
from root_tools import display, color565

class LightSensorTester(Tester):
    name = "Light Sensor"
    def draw_loading_bar(self, value):
        display.fill_rectangle(40, display.height - 80 - (50 * id), int(value * 240), 20, color565(255, 0, 0))
        display.fill_rectangle(40 + int(value * 240), display.height - 80 - (50 * id), 240 - int(value * 240), 20, color565(64, 64, 64))

    def init_loading_bar(self):
        display.fill_rectangle(40, display.height - 80, 240, 20, color565(64, 64, 64))
        display.fill_rectangle(40, display.height - 130, 240, 20, color565(64, 64, 64))

    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
        
 
    def start(self):    
        super().start()
        self.init_loading_bar()
        return True
       
    def test(self):
        for pin in self.pins:
            self.pot = ADC(Pin(pin))
            value = self.pot.read_u16()
            self.draw_loading_bar(pin - 27, value / 65535)

    def finish(self):
        super().finish()
        


