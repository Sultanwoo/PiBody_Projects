from tester.tester import Tester
from machine import Pin, I2C
from utime import sleep
from libs.VEML6040 import ColorSensor
from root_tools import *

class ColorTester(Tester):
    name = "Color Sensor"

    def __init__(self, pin):
            super().__init__(self.name, pin)
    
    def start(self):    
        super().start()

        if self.pin[0] == 0:
            bus = 0
        else:
            bus = 1

        for i in range(5): 
            try:
                self.veml = ColorSensor(bus, sda = self.pin[0], scl = self.pin[1])
                self.veml.readRGB()
                display.fill_rectangle(0, 90, display.width, 100, color565(0,0,0))
                return True
            except Exception as e:
                display.display_text(f"Sensor not found. Attempt {i + 1} in {5}. {e}", 20, 100)
                sleep(2)
        
        
        return False
        
    def test(self):
        try :
            rgb = self.veml.readRGB()
            r = rgb["red"]
            g = rgb["green"]
            b = rgb["blue"]
            a = rgb["white"]
        except Exception as e:
            print(e)
            print(self.veml.readRGB())
            r, g, b, a = "Error", "Error", "Error", "Error"
        # Print sensor readings
        display.display_text(f"red: {r}", 40, 100)
        display.display_text(f"green: {g}", 40, 130)
        display.display_text(f"blue: {b}", 40, 160)
        display.display_text(f"ambient: {a}", 40, 190)        

        print()

        sleep_ms(10)


    def finish(self):
        super().finish()