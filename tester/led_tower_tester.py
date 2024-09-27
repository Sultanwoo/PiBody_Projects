from tester.tester import Tester
from machine import Pin
from neopixel import NeoPixel
from root_tools import ctrl_button

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (128, 255, 128)]

    
class LedTowerTester(Tester):
    name = "LED Tower"
    def __init__(self, pin):
        super().__init__(self.name, pin)
        self.pin = pin


    def start(self):
        super().start()
        self.np = NeoPixel(Pin(self.pin), 8)
        return True

    def test(self):
        np = self.np
        for i in range(8):
            np[i] = colors[i]  # Set the current LED to red
            np.write()
        
        return True
            

    def finish(self):
        for i in range(8):
            self.np[i] = (0, 0, 0)
        self.np.write()
        super().finish()