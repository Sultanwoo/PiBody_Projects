from tester.tester import Tester
from machine import Pin, PWM, time_pulse_us, ADC, I2C, SoftI2C
from neopixel import NeoPixel
from root_tools import *
import time
from libs.rotary_irq_rp2 import RotaryIRQ
from libs.MPU6050 import MPU6050
from libs.BME280 import BME280

colors = [(40, 0, 0), (0, 40, 0), (0, 0, 40), (40, 40, 0), (0, 40, 40), (40, 0, 40), (40, 40, 40), (20, 40, 20)]
red = colors[0]
green = colors[1]


class LightTester(Tester):
    name = "Light Demo"

    def init_mpu(self, sda, scl):
        try:
            i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
            arr = i2c.scan() # takes some time to check for all addresses
            if 104 in arr:
                bus = 1
                if sda % 4 == 0:
                    bus = 0
                i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl))
                self.mpu = MPU6050(i2c=i2c)
                self.mpu.wake()
                return True
            return False
        except Exception as e:
            display.display_text(f"Sensor not found on GP{sda}. {e}", 20, 100)

    def init_climate(self, sda, scl):
        try:
            i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
            arr = []
            arr = i2c.scan() # takes some time to check for all addresses
            if 118 in arr:
                bus = 1
                if sda % 4 == 0:
                    bus = 0
                i2c = I2C(bus, sda=Pin(sda), scl=Pin(scl))
                self.bme280 = BME280(i2c=i2c)
                return True
            return False
        except Exception as e:
            display.display_text(f"Sensor not found on GP{sda}. {e}", 20, 100)

    def __init__(self, pin):
        super().__init__(self.name, pin)
        self.pin = pin

    def read_button_debounce(self, delayUntilStable) :
        reading = self.button.value()
        state = False
        if reading != self.lastButtonState:
            self.lastButtonStateChangeTime = time.ticks_ms()
        if time.ticks_ms() - self.lastButtonStateChangeTime > delayUntilStable:
            if reading != self.lastButtonStableState: 
                if reading: 
                    state = True
                self.lastButtonStableState = reading
        self.lastButtonState = reading
        return state

    def read_temp(self):
        try:
            self.init_climate(6, 7)
            temp = self.bme280.temperature
            temp = float(temp[0:4])
        except Exception as e:
            print("An error occurred:", e)
            temp = 23
        return temp

    def start(self):
        super().start()
        self.np = NeoPixel(Pin(self.pin), 8)
        self.led = PWM(Pin(0, Pin.OUT))
        self.led.freq(1000)
        self.button = Pin(1, Pin.IN)
        self.touch = Pin(2, Pin.IN)
        self.potentiometer = ADC(Pin(28))
        self.encoder = RotaryIRQ(16, 17, min_val=0, max_val=7, incr=1, reverse=False, range_mode=RotaryIRQ.RANGE_WRAP)
        self.counter = 0

        self.sound_analog = ADC(Pin(26))
        self.sound_digital = Pin(27, Pin.IN)

        self.mode = 'static'
        self.lastButtonState = False
        self.lastButtonStableState = False 
        self.lastButtonStateChangeTime = 0 
        self.lastTouchStateChangeTime = 0
        self.init_mpu(4, 5)
        self.init_climate(6, 7)

        self.min_temp = self.read_temp()
        self.max_temp = self.min_temp + 3

        return True

    def test(self):
        np = self.np
        max_pv = 65536

        try:
            gyro = self.mpu.read_gyro_data()
            accel = self.mpu.read_accel_data()
        except Exception as e:
            gyro = (0, 0, 0)
            accel = (0, 0, 0)
            print("An error occurred:", e)
            self.init_mpu(4, 5)

        a = -accel[1]
        s = self.sound_analog.read_u16()
        pv = self.potentiometer.read_u16()
        temp = self.read_temp()
        brightness = pv / max_pv * 0.8 + 0.2
        state = self.read_button_debounce(50)
        # print("Accelerometer:", a)
        # print("Temperature:", temp, self.min_temp, self.max_temp)
        # print("Sound:", s)
        # print("Brightness:", brightness)

        if abs(a) > 0.1 :
            self.encoder.set(int((a + 1.0) / 2 * 8))

        if s > 1000 :
            self.mode = 'sound'
        else :
            self.mode = 'counter'

        new_counter = self.encoder.value()
        if new_counter == 1 :
            self.led.duty_u16(int(max_pv * brightness / 2))
        else :
            self.led.duty_u16(0)
        if self.touch.value() and time.ticks_ms() - self.lastTouchStateChangeTime > 250 :
            self.mode = 'counter'
            self.encoder.set((self.counter + 1) % 8)
            self.lastTouchStateChangeTime =  time.ticks_ms()
        if state :
            self.mode = 'counter'
            self.encoder.set((self.counter + 1) % 8)
        elif new_counter != self.counter :
            self.mode = 'counter'
            self.counter = new_counter

        if self.mode == 'counter' :
            temp = max(temp, self.min_temp)
            temp = min(temp, self.max_temp)
            redness = (temp - self.min_temp) / (self.max_temp - self.min_temp)
            for i in range(8):
                if i == self.counter :
                    np[i] = (int(colors[i][0] * brightness * (1-redness) + 40 * brightness * redness), 
                             int(colors[i][1] * brightness * (1-redness)),  
                             int(colors[i][2] * brightness * (1-redness)))
                else :
                    np[i] = (0, 0, 0)
                np.write()
        elif self.mode == 'sound' :
            leds = min(int(s / max_pv * 8), self.encoder.value())
            for i in range(leds):
                np[i] = (int(colors[i][0] * brightness),  int(colors[i][1] * brightness),  int(colors[i][2] * brightness))
                np.write()

        return True


    def finish(self):
        for i in range(8):
            self.np[i] = (0, 0, 0)
        self.np.write()
        super().finish()
