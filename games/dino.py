from machine import Pin, SPI, PWM, freq, ADC
from utime import sleep_ms, ticks_ms, ticks_diff
from libs.ILI9341 import Display, color565
import urandom

# Set the CPU frequency
freq(270000000)

# Initialize SPI and Display with corrected pin settings
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(14), cs=Pin(15), rst=Pin(13), width=320, height=240)
display.clear()

# Initialize button
button = Pin(2, Pin.IN, Pin.PULL_DOWN)
pot = ADC(28)
# Initialize PWM for sound effects
buzzer = PWM(Pin(12))  # Use a pin connected to a buzzer

# Sound frequencies for the game
jump_sound_freq = 1000  # Frequency for jump sound
game_over_sound_freq = 400  # Frequency for game over sound
sound_duration = 100  # Duration of sound in milliseconds

# Colors
bg_color = color565(0, 0, 0)        # Background color (black)
dino_color = color565(255, 255, 255) # Dino color (white)
obstacle_color = color565(0, 255, 0) # Obstacle color (green)
score_color = color565(255, 255, 0)  # Score color (yellow)
text_color = color565(255, 255, 255) # Game over text color (white)
ground_color = color565(139, 69, 19) # Ground line color (brown)
skyline_color = color565(135, 206, 235) # Skyline color (sky blue)
ground_y = 200                      # Ground position

# 40x39 Dino bitmap representation
dino_bitmap = [
    "0000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000",
    "0000000000000000000000111111111111110000",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011110011111111111100",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011111111111111111100",
    "0000000000000000000011111111110000000000",
    "0000000000000000000011111111110000000000",
    "0000000000000000000011111111110000000000",
    "0000000000000000000011111111000000000000",
    "0000000000000000000011111111000000000000",
    "0000000000000000000011111111000000000000",
    "0000000000000000000011111111000000000000",
    "0000000000000000000011111111100000000000",
    "0000001000000000000111111111111100000000",
    "0000001000000000011111111111000100000000",
    "0000001100000001111111111111000000000000",
    "0000001100000011111111111111000000000000",
    "0000001111000111111111111111000000000000",
    "0000001111111111111111111111000000000000",
    "0000001111111111111111111111000000000000",
    "0000001111111111111111111110000000000000",
    "0000001111111111111111111100000000000000",
    "0000000111111111111111111000000000000000",
    "0000000011111111111111110000000000000000",
    "0000000001111111111001100000000000000000",
    "0000000000001111111001100000000000000000",
    "0000000000001111110001100000000000000000",
    "0000000000000111000001100000000000000000",
    "0000000000000111000000100000000000000000",
    "0000000000000110000000100000000000000000",
    "0000000000000010000000100000000000000000",
    "0000000000000011000000111000000000000000",
    "0000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000",
]

# Convert the Dino bitmap to a buffer once
def dino_to_buffer(color):
    buffer = bytearray()
    for row in dino_bitmap:
        for pixel in row:
            if pixel == '1':
                buffer.extend(color.to_bytes(2, 'big'))  # White for Dino
            else:
                buffer.extend(bg_color.to_bytes(2, 'big'))  # Black for background
    return buffer

# Create the Dino buffer once with the dino color
dino_buffer = dino_to_buffer(dino_color)
clear_buffer = dino_to_buffer(bg_color)  # Buffer for clearing the Dino

# Function to draw the Dino using the block function
def draw_dino(x, y, clear=False):
    if clear:
        display.block(x, y, x + 39, y + 38, clear_buffer)  # Use clear buffer
    else:
        display.block(x, y, x + 39, y + 38, dino_buffer)  # Use pre-generated Dino buffer

# Function to draw the obstacle
def draw_obstacle(x, y):
    display.fill_vrect(x, y, obstacle_width, obstacle_height, obstacle_color)

# Function to clear the obstacle
def clear_obstacle(x, y):
    display.fill_vrect(x, y, obstacle_width, obstacle_height, bg_color)

def map_value(value, from_min, from_max, to_min, to_max):
    # Calculate the scaled value within the target range
    return to_min + (value - from_min) * (to_max - to_min) // (from_max - from_min)
# Function to play a sound
def play_sound(frequency, duration):
    pot_value = pot.read_u16()
    duty = map_value(pot_value, 0, 65535, 100, 10000)
    buzzer.freq(frequency)
    buzzer.duty_u16(duty)  # 50% duty cycle for sound
    sleep_ms(duration)
    buzzer.duty_u16(0)  # Stop sound

# Obstacle variables
obstacle_x = 320
obstacle_y = ground_y - 20
obstacle_width = 10
obstacle_height = 20
obstacle_speed = 5

# Game variables
score = 0
game_over_flag = False
game_speed = 1  # Initial game speed multiplier
speed_increment_interval = 5  # Increase speed every 5 obstacles
next_speed_increase = speed_increment_interval

# Spacing options for obstacles
obstacle_spacing_options = [100, 150, 200, 250]

# Dino jump variables
jump_height = 50  # Set the peak jump height
jump_suspension_time = 300  # Time in milliseconds to suspend at peak
jumping = False
falling = False
suspending = False  # New state for suspending at peak
jump_start = 0
jump_speed = 5  # Same speed for upward and downward movement

# Updated byte array for "GAME OVER" message in 8x8 bitmap format (scaled up)
game_over_bitmap = [
    # G (updated to be bolder)
    0b00111100, 0b01111110, 0b01100000, 0b01100000, 0b01101110, 0b01100110, 0b00111100, 0b00000000,
    # A
    0b00011000, 0b00111100, 0b01100110, 0b01100110, 0b01111110, 0b01100110, 0b01100110, 0b00000000,
    # M
    0b01100011, 0b01110111, 0b01111111, 0b01101011, 0b01100011, 0b01100011, 0b01100011, 0b00000000,
    # E
    0b01111110, 0b01100010, 0b01101000, 0b01111000, 0b01101000, 0b01100010, 0b01111110, 0b00000000,
    # Space
    0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000, 0b00000000,
    # O
    0b00111100, 0b01100110, 0b01100110, 0b01100110, 0b01100110, 0b01100110, 0b00111100, 0b00000000,
    # V
    0b01100110, 0b01100110, 0b01100110, 0b01100110, 0b01100110, 0b00111100, 0b00011000, 0b00000000,
    # E
    0b01111110, 0b01100010, 0b01101000, 0b01111000, 0b01101000, 0b01100010, 0b01111110, 0b00000000,
    # R
    0b01111100, 0b01100110, 0b01100110, 0b01111100, 0b01101100, 0b01100110, 0b01100110, 0b00000000,
]

# Function to display a large "GAME OVER" message using the bitmap
def draw_large_bitmap(x, y, bitmap, color, scale=3):
    for char_index in range(len(bitmap) // 8):
        char_x = x + char_index * 8 * scale
        for row in range(8):
            row_data = bitmap[char_index * 8 + row]
            for col in range(8):
                if row_data & (1 << (7 - col)):  # Check each bit
                    display.fill_vrect(char_x + col * scale, y + row * scale, scale, scale, color)

# Function to display game over message with score
def display_game_over():
    play_sound(game_over_sound_freq, sound_duration)  # Play game over sound
    display.clear()
    draw_large_bitmap(60, 80, game_over_bitmap, text_color, scale=3)  # Draw the "GAME OVER" bitmap
    display.draw_text8x8(130, 140, f"Score: {score}", color565(255, 255, 0))  # Yellow score text
    sleep_ms(2000)  # Rest for 2 seconds before restarting
    reset_game()

# Function to reset the game
def reset_game():
    global dino_y, jumping, falling, suspending, obstacle_x, score, game_over_flag, game_speed, next_speed_increase
    dino_y = ground_y - 39
    jumping = False
    falling = False
    suspending = False
    obstacle_x = 320
    score = 0
    game_speed = 1
    next_speed_increase = speed_increment_interval
    game_over_flag = False
    display.clear()
    draw_dino(dino_x, dino_y)  # Ensure Dino is drawn initially
    draw_ground()  # Draw the ground lines
    draw_skyline()  # Draw the upper skyline

# Function to display the current score at the top, centered
def display_score():
    display.fill_vrect(0, 0, 320, 16, bg_color)  # Clear previous score
    display.draw_text8x8(130, 10, f"Score: {score}", score_color)  # Centered score display

# Function to draw the ground lines
def draw_ground():
    for i in range(ground_y, ground_y + 10, 2):  # Draw ground line near the Dino
        display.draw_hline(0, i, 320, ground_color)

# Function to draw the upper skyline
def draw_skyline():
    for i in range(0, 10, 2):  # Draw skyline lines at the top
        display.draw_hline(0, i, 320, skyline_color)

# Initial drawing
dino_x = 50
dino_y = ground_y - 39
draw_dino(dino_x, dino_y)
draw_obstacle(obstacle_x, obstacle_y)
display_score()
draw_ground()  # Draw the ground lines
draw_skyline()  # Draw the upper skyline

# Main game loop
while True:
    # Handle button input for jumping
    if button.value() and not jumping and not falling and not suspending and not game_over_flag:
        jumping = True
        jump_start = ticks_ms()
        play_sound(jump_sound_freq, sound_duration)  # Play jump sound

    # Dino jumping logic
    if jumping:
        draw_dino(dino_x, dino_y, clear=True)  # Clear previous position
        dino_y -= jump_speed  # Move up incrementally
        draw_dino(dino_x, dino_y)
        if dino_y <= ground_y - 39 - jump_height:
            jumping = False
            suspending = True
            jump_start = ticks_ms()  # Reset time for suspension

    # Suspension logic
    if suspending:
        if ticks_diff(ticks_ms(), jump_start) > jump_suspension_time:
            suspending = False
            falling = True

    # Dino falling logic
    if falling:
        draw_dino(dino_x, dino_y, clear=True)  # Clear previous position
        dino_y += jump_speed  # Fall incrementally
        draw_dino(dino_x, dino_y)
        if dino_y >= ground_y - 39:
            falling = False
            dino_y = ground_y - 39  # Correct position at ground level

    # Move the obstacle
    clear_obstacle(obstacle_x, obstacle_y)
    obstacle_x -= int(obstacle_speed * game_speed)  # Speed up obstacle
    if obstacle_x < -obstacle_width:
        obstacle_x = 320 + urandom.choice(obstacle_spacing_options)  # Randomize obstacle spacing
        score += int(game_speed)  # Increase score by speed multiplier
        display_score()  # Update the score display

        # Increment game speed
        if score >= next_speed_increase:
            game_speed += 0.1  # Gradually increase speed
            next_speed_increase += speed_increment_interval  # Set next score threshold for speed increase

    # Draw the obstacle
    draw_obstacle(obstacle_x, obstacle_y)

    # Check for collision
    if (dino_x < obstacle_x + obstacle_width and
        dino_x + 40 > obstacle_x and
        dino_y < obstacle_y + obstacle_height and
        dino_y + 39 > obstacle_y):
        game_over_flag = True
        display_game_over()

    # End game if over
    if game_over_flag:
        sleep_ms(2000)  # Pause before restarting the game
        reset_game()

    # Update display and game speed
    sleep_ms(int(30 / game_speed))  # Decrease delay as speed increases
