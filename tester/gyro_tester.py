from tester.tester import Tester
from machine import Pin, I2C, SoftI2C
from utime import sleep, sleep_ms
from libs.MPU6050 import MPU6050
from root_tools import *

class GyroTester(Tester):
    name = "Gyroscope + Accelerometer"
    border_tl = (50, 80)
    border_br = (220, 110)
    prev_x = 150
    prev_y = 150
    x = 150
    y = 150
    dx = 0
    dy = 0
    accel_x = 0
    accel_y = 0

    def __init__(self, pins):
        super().__init__(self.name, pins)
        self.pins = pins
    
    def border(self):
        border_tl = self.border_tl
        border_br = self.border_br
        display.draw_rectangle(border_tl[0] - 1, border_tl[1] - 1, border_br[0] + 3, border_br[1] + 3, color565(255, 255, 255))

    def init_I2C(self, sda, scl):
        try:
            i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
            arr = i2c.scan() # takes some time to check for all addresses
            if 104 in arr:
                print(arr)
                bus = 1
                if sda % 4 == 0:
                    bus = 0
                i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl))
                self.mpu = MPU6050(i2c=i2c)
                self.mpu.wake()
                display.fill_rectangle(0, 90, display.width, 100, color565(0,0,0))
                self.border()
                return True
            return False
        except Exception as e:
            display.display_text(f"Sensor not found on GP{sda}. {e}", 20, 100)
            sleep(1)

    def start(self):    
        super().start()
        for i in range(4): 
            if self.init_I2C(self.pins[i*2], self.pins[i*2+1]):
                return True
        return False
        
    def show(self):
        #display.fill_circle(int(self.x), int(self.y), 5, color565(255, 255, 0))
        display.fill_rectangle(int(self.x)-5, int(self.y-5), 11, 11, color565(255, 255, 0))

    def unshow(self):
        if not (self.prev_x == self.x and self.prev_y == self.y):
            display.fill_rectangle(int(self.prev_x)-5, int(self.prev_y)-5, 11, 11, color565(0, 0, 0))

    def move(self):
        border_tl = self.border_tl
        border_br = self.border_br
        self.velocity_vector()
        t = border_tl[1] + 5 
        b = border_br[1] + border_tl[1] - 5
        l = border_tl[0] + 5
        r = border_br[0] + border_tl[0] - 5
        
        if self.x + self.dx > r:
            self.prev_x = self.x
            self.x = r
            self.dx = 0
        elif self.x + self.dx < l:
            self.prev_x = self.x
            self.x = l
            self.dx = 0
        else:
            self.prev_x = self.x
            self.x += self.dx

        if self.y + self.dy > b:
            self.prev_y = self.y
            self.y = b
            self.dy = 0
        elif self.y + self.dy < t:
            self.prev_y = self.y
            self.y = t
            self.dy = 0
        else: 
            self.prev_y = self.y
            self.y += self.dy

    def velocity_vector(self):
        sens = 0.7 #sensitivity
        self.dx += self.accel_x * sens
        self.dy += self.accel_y * sens
        if abs(self.dx) < 0.02:
            self.dx = 0
        if abs(self.dy) < 0.02: 
            self.dy = 0

    def test(self):
        try:
            gyro = self.mpu.read_gyro_data()
            accel = self.mpu.read_accel_data()
        except Exception as e:
            gyro = (0, 0, 0)
            accel = (0, 0, 0)
            print("An error occurred:", e)
            #self.mpu = MPU6050(i2c=self.i2c)
            #self.mpu.wake()
            sleep(1)
        self.accel_x = -accel[1]
        self.accel_y = -accel[0]
        #display.display_text(f"Gyroscope", 50, 20)
        #display.display_text(f"x:{gyro[0] :.3f} y:{gyro[1] :.3f} z:{gyro[2] :.3f}", 40, 30)
        #display.display_text(f"Accelerometer", 60, 50)
        #display.display_text(f"x:{accel[1] :.3f} y:{accel[0] :.3f} z:{accel[2] :.3f}", 40, 60)
        
        self.move()
        self.unshow()
        self.show()
        sleep_ms(0)


    def finish(self):
        super().finish()