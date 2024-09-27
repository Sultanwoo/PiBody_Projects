from machine import Pin
from utime import sleep_ms
from root_tools import display, right_btn, up_btn, left_btn, down_btn, color565
import os

GAMES_QUANTITY = 3# Currently only 3 games are supported

contents = os.listdir('/games')
games = [f for f in contents if f.endswith('.py')]
games = games[:GAMES_QUANTITY] 
games_names = [name[:-3] for name in games]

print(games_names)

block_width = (display.width - 30) // 3
block_height = display.height

def frame(cnt, color, frame_color):
    display.text_box(games_names[cnt], 15 + (cnt % GAMES_QUANTITY) * block_width, 0, w = block_width, h = block_height, text_color= color, color = color)
    for i in range(1, 10):
        display.draw_rectangle(
            15 + cnt * block_width + i, 
            0 + i, 
            block_width - 2 * i, 
            block_height - 2 * i, 
            frame_color
            )

def select_cell(cnt):
    frame(cnt, color565(80, 80, 0), color565(80, 80, 0))

def deselect_cell(cnt):
    frame(cnt, color565(255, 255, 255), color565(0, 0, 0))

def main_menu():
    global test_list
    display.clear()

    for i in range(3):
        x = 15 + i * block_width
        y = 0
        display.text_box(games_names[i], x, y, w = block_width, h = block_height)

movement = 0
def callback(p):
    global movement
    movement = p

# main.py
def run_another_file(ind):
    with open(f"games/{games[ind]}") as f:
        code = f.read()
        exec(code)

selected_cell = 0
is_launched = 0

def launch_game():
    global is_launched
    is_launched = 1

def main():
    global selected_cell, movement
    main_menu()

    left_btn.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(-1))
    right_btn.irq(trigger=Pin.IRQ_RISING, handler=lambda a:callback(+1))
    up_btn.irq(trigger=Pin.IRQ_RISING, handler=lambda a:launch_game())
    

    select_cell(selected_cell)
    while True:
        if is_launched:
            run_another_file(selected_cell)

        if not movement:
            continue
        selected_cell = (selected_cell + movement) % GAMES_QUANTITY
        select_cell(selected_cell)
        deselect_cell((selected_cell - movement) % GAMES_QUANTITY)
        movement = 0


main()