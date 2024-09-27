from tester.tester import Tester
from machine import Pin, I2C
from utime import sleep
from libs.PAJ7620 import Gesture
from root_tools import *

class GestureTester(Tester):
    name = "Gesture Sensor"
    last_value =  - 2
    def __init__(self, pin):
            super().__init__(self.name, pin)
    
    def start(self):    
        super().start()

        if self.pin[0] == 0:
            bus = 0
        else:
            bus = 1
        i2c = I2C(bus, sda=Pin(self.pin[0]), scl=Pin(self.pin[1]))

        for i in range(5): 
            try:
                self.paj7620 = Gesture(i2c=i2c)
                self.paj7620.return_gesture()
                display.fill_rectangle(0, 90, display.width, 100, color565(0,0,0))
                return True
            except Exception as e:
                display.display_text(f"Sensor not found. Attempt {i + 1} in {5}. {e}", 20, 100)
                sleep(2)
        
        
        return False
        
    def test(self):
        try :
            value = self.paj7620.return_gesture()
        except:
            value = -1
        # Print sensor readings

        gesture_names = [
            "in",
            "out",
            "left",
            "right",
            "down",
            "up",
            "clockwise",
            "counterclockwise",
            "wave"
        ]
        if value > 0:
            if value != self.last_value:
                display.fill_rectangle(40, 100, 240, 30, color565(0, 0, 0))
                display.display_text(f"Gesture: {gesture_names[value - 1]}", 40, 100)
                self.last_value = value


        print()

        sleep_ms(10)


    def finish(self):
        super().finish()