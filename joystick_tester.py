from tester.tester import Tester
from machine import Pin, ADC
from utime import sleep_ms

from root_tools import *

from libs.rotary_irq_rp2 import RotaryIRQ


class JoystickTester(Tester):
    name = "Joystick"
    border_tl = (50, 80)
    border_br = (210, 140)
    x = 130
    y = 110

    def __init__(self, pin):
            super().__init__(self.name, pin)
    
    def border(self):
        border_tl = self.border_tl
        border_br = self.border_br
        display.draw_rectangle(border_tl[0] - 1, border_tl[1] - 1, border_br[0] + 1, border_br[1] + 1, color565(255, 255, 255))

    def clear(self):
        border_tl = self.border_tl
        border_br = self.border_br
        display.fill_rectangle(border_tl[0], border_tl[1], border_br[0], border_br[1], color565(255, 255, 255))

    def start(self):    
        super().start()
        self.clear
        self.joy_x = ADC(Pin(self.pin[0]))
        self.joy_y = ADC(Pin(self.pin[1]))

        self.border()
        return True

    def show(self):
         display.fill_circle(int(self.x), int(self.y), 5, color565(255, 0, 0))
    
    def move(self, dx, dy):
        border_tl = self.border_tl
        border_br = self.border_br
        t = border_tl[1] + 5 
        b = border_br[1] + border_tl[1] - 5 
        l = border_tl[0] + 5
        r = border_br[0] + border_tl[0] - 5

        if self.x + dx > r or self.x + dx < l:
            dx = 0
        if self.y + dy > b or self.y + dy < t:
            dy = 0
        self.x += dx
        self.y += dy

    

    def velocity_vector(self):

        
        dx = self.joy_x.read_u16() / 65535
        dy = self.joy_y.read_u16() / 65535
        dx = (dx - 0.5)
        dy = (dy - 0.5)
        if abs(dx) < 0.1:
            dx = 0
        if abs(dy) < 0.1: 
            dy = 0    

        return(dx * 5, dy * 5)

    def test(self):
       if ctrl_button.value():
           self.clear()
           return

       self.move(*self.velocity_vector())
       self.show()
        # Optional debounce delay

# Set up the encoder pins

# Initialize counter and previous state variable
