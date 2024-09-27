from tester.tester import Tester
from machine import Pin, ADC
from utime import sleep
from root_tools import display, color565

class PotentiometerTester(Tester):
    name = "Potentiometer and Light Sensor"
    def draw_loading_bar0(self, value):
        display.fill_rectangle(40, display.height - 80 - (50), int(value * 240), 20, color565(255, 10, 128))
        display.fill_rectangle(40 + int(value * 240), display.height - 80 - (50), 240 - int(value * 240), 20, color565(64, 64, 64))

    def draw_loading_bar1(self, value):
        display.fill_rectangle(40, display.height - 80, int(value * 240), 20, color565(255, 10, 128))
        display.fill_rectangle(40 + int(value * 240), display.height - 80, 240 - int(value * 240), 20, color565(64, 64, 64))
        
    def init_loading_bar(self):
        display.fill_rectangle(40, display.height - 80, 240, 20, color565(64, 64, 64))
        display.fill_rectangle(40, display.height - 130, 240, 20, color565(64, 64, 64))
        display.display_text("GP28", 40, display.height - 150)
        display.display_text("GP27", 40, display.height - 100)

    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
 
    def start(self):    
        super().start()
        self.init_loading_bar()
        self.pot0 = ADC(Pin(self.pins[0]))
        self.pot1 = ADC(Pin(self.pins[1]))
        return True
       
    def test(self):
        value0 = self.pot0.read_u16() / 65535
        value1 = self.pot1.read_u16() / 65535
        #print(f"V0:{value0}\nV1:{value1}")
        self.draw_loading_bar0(value0)
        self.draw_loading_bar1(value1)

    def finish(self):
        super().finish()
        


