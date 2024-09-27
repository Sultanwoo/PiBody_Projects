from machine import Pin, PWM
from time import sleep_ms
from math import sin, pi

full = [0, 1, 5, 7, 2, 28, 17, 27] # pin list
for i in range(2000): # number of pulses multiplied by 10
    for pin in full:
        led = PWM(Pin(pin), freq=100) # initializing pin 
        value = int(sin(i / 10 * pi) * 30000 + 45000)
        led.duty_u16(value) # maximum duty is ~65000, anything above is clipped
        print(value)
    sleep_ms(50) # latency

