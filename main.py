from machine import Pin, PWM
from utime import sleep_ms, ticks_ms, sleep
from root_tools import display, ctrl_button, up_button, left_button, down_button, color565
from all_testers import test_list
from neopixel import NeoPixel # tower

buzzer = PWM(Pin(12))
C4 = 261
D4 = 294
E4 = 329
F4 = 349
G4 = 392
A4 = 440
B4 = 493
C5 = 523
melody = [D4,C4, E4]
durations = [0.5, 0.5, 0.5]  
def play_tone(frequency, duration):
    buzzer.freq(frequency)
    buzzer.duty_u16(256)  # 1024 = 12.5%/8 duty cycle
    sleep(duration)
    buzzer.duty_u16(0)
for note, duration in zip(melody, durations):
    play_tone(note, duration)

test_ind = 0
hold_duration = 750

def start_test(ind):
    if test_ind != 0:
        test_list[test_ind - 1].finish()
    display.clear()
    current_test = test_list[ind]
    return current_test.start()

def menu_loading_bar(value):
    display.fill_rectangle(280 - int(value * 240), 50, int(value * 240), 10, color565(128, 255, 0))

def draw_loading_bar(value):
    display.fill_rectangle(40, 50, int(value * 240), 10, color565(128, 255, 0))

def init_loading_bar():
    display.fill_rectangle(40, 50, 240, 10, color565(64, 64, 64))

all = [0, 1, 2, 28, 5, 7, 17, 27]
colors = [(50, 0, 0), (33, 16, 0), (25, 25, 0), (0, 50, 0), (0, 25, 25), (0, 0, 50), (25, 0, 25), (25, 25, 25)] # rainbow + white
def init():
    display.clear()
    np = NeoPixel(Pin(22), 8)
    for pin in all:
            led = Pin(pin, Pin.OUT)
            led.value(0)
    display.display_text("Navigate by pressing", 40, 76)
    display.display_text("GPs 18, 19, 20 and 21.", 50, 86)
    display.display_text("Select a test by holding any.", 40, 96)
    display.display_text("Press any button to continue", 40, 156)

    for i in range(8):
        np[i] = colors[i]  # Set the current LED to red
    np.write()

    while not (ctrl_button.value() or up_button.value() or left_button.value() or down_button.value()):
        pass

    for i in range(8):
        np[i] = (0, 0, 0)
    np.write()

menu_options = [tester.name for tester in test_list]

def select_cell(cnt):
    display.text_box(menu_options[cnt], 20 + (cnt % 3) * 94, (cnt // 3) * 80, w = 94, h = 80, text_color= color565(20, 20, 0), color= color565(80, 80, 0))
# (b, g, r)
def deselect_cell(cnt):
    display.text_box(menu_options[cnt], 20 + (cnt % 3) * 94, (cnt // 3) * 80, w = 94, h = 80)

movement = 0
def callback(p):
    global movement
    movement = p

def menu():
    global test_list
    display.clear()
    for i in range(3):
        for j in range(3):
            display.text_box(menu_options[i * 3 + j], 20 + j * 94, i * 80, w = 94, h = 80)
    
    selected_cell = 0
    select_cell(selected_cell)

    up_button.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(-3))
    left_button.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(-1))
    down_button.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(+3))
    ctrl_button.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(+1))
    
    while True:
        global movement
        if movement:
            hold_time_elapsed = ticks_ms()
            while up_button.value() or left_button.value() or ctrl_button.value() or down_button.value():
                if ticks_ms() - hold_time_elapsed > hold_duration:
                    print("Selected test: ", menu_options[selected_cell])
                    test_list = test_list[selected_cell:9]
                    return
            selected_cell = (selected_cell + movement) % 9
            select_cell(selected_cell)
            deselect_cell((selected_cell - movement) % 9)
            movement = 0
        
def main():
    global test_ind
    
    init()

    hold_time_elapsed = ticks_ms()

    menu()

    test_count = len(test_list)

    while not start_test(test_ind):
        test_ind = (test_ind + 1) % len(test_list)

    init_loading_bar()
    hold_time_elapsed = ticks_ms()
    while True:
        if ctrl_button.value():
            if ticks_ms() - hold_time_elapsed > hold_duration:
                test_ind += 1
                print(test_ind)
                if test_ind == len(test_list):
                    display.clear()
                    display.display_text("All tests passed!", 0, 116)
                    return
                                      
                while not start_test(test_ind):
                    test_ind = (test_ind + 1) % len(test_list)
                
                hold_time_elapsed = ticks_ms()
                print("Ticked")
            else:
                draw_loading_bar((ticks_ms() - hold_time_elapsed) / hold_duration)
        else:
            hold_time_elapsed = ticks_ms()
            init_loading_bar()
            test_list[test_ind].test()
main()