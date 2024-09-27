from tester.tester import Tester
from machine import Pin, I2C, SoftI2C
from utime import sleep
from libs.BME280 import BME280
from root_tools import *

class ClimateTester(Tester):
    name = "Climate Sensor"

    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins

    def init_I2C(self, sda, scl):
        try:
            i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
            arr = []
            arr = i2c.scan() # takes some time to check for all addresses
            if 118 in arr:
                print(arr)
                bus = 1
                if sda % 4 == 0:
                    bus = 0
                i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl))
                self.bme280 = BME280(i2c=i2c)
                self.bme280.temperature
                display.fill_rectangle(0, 90, display.width, 100, color565(0,0,0))
                return True
            return False
        except Exception as e:
            display.display_text(f"Sensor not found on GP{sda}. {e}", 20, 100)
            sleep(1)

    def start(self):    
        super().start()        
        for i in range(4):
            display.display_text(f"Scanning GP{self.pins[i*2+1]}", 30, 100)
            if self.init_I2C(self.pins[i*2], self.pins[i*2+1]):
                return True
        return False
        
    def test(self):
        try :
            temp = self.bme280.temperature
            hum = self.bme280.humidity
            pres = self.bme280.pressure
        except:
            temp = 0
            hum = 0
            pres = 0
        # Print sensor readings
        display.display_text(f"Temperature: {temp}", 40, 100)
        display.display_text(f"Humidity: {hum}", 40, 130)
        display.display_text(f"Pressure: {pres}", 40, 160)

        sleep_ms(10)

    def finish(self):
        super().finish()