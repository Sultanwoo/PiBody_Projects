from machine import Pin, SPI
from utime import sleep_ms  

from libs.ILI9341 import Display, color565


last_text = ""
def draw_loading_bar(value):
    display.fill_rectangle(40, display.height - 80, int(value * 240), 20, color565(255, 10, 128))
    display.fill_rectangle(40 + int(value * 240), display.height - 80, 240 - int(value * 240), 20, color565(64, 64, 64))

def init_loading_bar():
    display.fill_rectangle(40, display.height - 80, 240, 20, color565(64, 64, 64))

def display_info(text):
    global last_text
    if text == last_text:
        return
    display.fill_rectangle(0, display.height - 40, display.width, 40, color565(0,0,0))
    display.display_text(text, 0, display.height - 40)
    last_text = text

def initialize_display():
    spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
    display = Display(spi, dc=Pin(14), cs=Pin(15), rst=Pin(13), width=320, height=240)
    display.clear()
    return display

def show_circile(value):
    display.fill_circle(display.width // 2, display.height  - 40, 10,  color565(0, value * 255, 0))

up_button = Pin(18, Pin.IN, Pin.PULL_DOWN)
left_button = Pin(21, Pin.IN, Pin.PULL_DOWN)
down_button = Pin(20, Pin.IN, Pin.PULL_DOWN)
ctrl_button = Pin(19, Pin.IN, Pin.PULL_DOWN)
display = initialize_display()
    
