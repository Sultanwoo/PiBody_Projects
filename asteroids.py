from machine import Pin, SPI, ADC, freq, PWM
from utime import sleep_ms, ticks_ms, ticks_diff
from libs.ILI9341 import Display, color565
import urandom

# Set the CPU frequency
freq(270000000)

# Initialize SPI and Display with corrected pin settings
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(14), cs=Pin(15), rst=Pin(13), width=320, height=240)
# Colors with reversed intensity
bg_color = color565(255, 255, 255)     # Background color (black)
spaceship_color = color565(255, 0, 0)  # Spaceship color (yellow)
asteroid_color = color565(0, 0, 0)     # Asteroid color (white)
text_color = color565(0, 0, 0)         # Text color (white)
score_color = color565(0, 0, 0)        # Score color (white)


# Clear display to black color
display.clear(color=bg_color)

# Initialize input
pot = ADC(26)  # Potentiometer to control spaceship movement

# Initialize buzzer
buzzer = PWM(Pin(12))
buzzer.duty_u16(0)  # Start with buzzer off

# Improved Melody notes and timings (frequency, duration in milliseconds)
melody = [
    (523, 100), (659, 100), (784, 100), (1047, 100), (0, 50),  # Upward scale
    (1047, 100), (784, 100), (659, 100), (523, 100), (0, 50),  # Downward scale
    (659, 100), (784, 100), (988, 100), (1047, 100), (880, 100), (784, 100), (659, 100), (523, 100), (0, 50),  # More complex sequence
    (784, 100), (880, 100), (988, 100), (1047, 200), (0, 100),  # Short pause
    (523, 100), (784, 100), (659, 200), (523, 100), (0, 50),  # Varied rhythm
]

# Variables for melody playback
melody_index = 0
last_note_time = ticks_ms()

# Spaceship variables
spaceship_width = 50
spaceship_height = 50
spaceship_y = 190  # Position near the bottom of the screen
spaceship_x = (320 - spaceship_width) // 2  # Start in the center of the screen
center_threshold = 28000  # Midpoint value for 16-bit ADC
deadzone = 5000  # Range around center where no movement occurs
steering_sensitivity = 5000  # Sensitivity factor for steering speed

# Asteroid variables
asteroids = []  # List to hold active asteroids
asteroid_spawn_interval = 1000  # Time in milliseconds between spawns
last_asteroid_spawn = ticks_ms()  # Initialize with the current time

# Game variables
score = 0
game_over_flag = False
game_speed = 1  # Initial game speed multiplier

# Spaceship bitmap (50x50 pixels)
spaceship_bitmap = [
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000011000000000000000000000000",
    "00000000000000000000000011000000000000000000000000",
    "00000000000000000000000111100000000000000000000000",
    "00000000000000000000000111100000000000000000000000",
    "00000000000000000000000100100000000000000000000000",
    "00000000000000000000000100100000000000000000000000",
    "00000000000000000000001100110000000000000000000000",
    "00000000000000000000001100110000000000000000000000",
    "00000000000000000000011100111000000000000000000000",
    "00000000000000000000011100111000000000000000000000",
    "00000000000000000000011100111000000000000000000000",
    "00000000000000000000011100111000000000000000000000",
    "00000000000000000000011111111000000000000000000000",
    "00000000000000000000001111110000000000000000000000",
    "00000000000000000000001111110000000000000000000000",
    "00000010000000000000001111110000000000000001000000",
    "00000010000000000000001111110000000000000001000000",
    "00000010100000000000001111110000000000000101000000",
    "00000010100000000000000111100000000000000101000000",
    "00000010101000000000000111100000000000010101000000",
    "00000010101000000111111111111111100000010101000000",
    "00000011111111111111111111111111111111111111000000",
    "00000011111111111111111111111111111111111111000000",
    "00000011111111111111111111111111111111111111000000",
    "00000000111111111111111111111111111111111100000000",
    "00000000001111111111111111111111111111110000000000",
    "00000000001011111111111111111111111111010000000000",
    "00000000001000111000000111100000011100010000000000",
    "00000000000000100000011111111000000100000000000000",
    "00000000000000100011111111111111000100000000000000",
    "00000000000000000011111100111111000000000000000000",
    "00000000000000000001110000001110000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
    "00000000000000000000000000000000000000000000000000",
]

# Convert spaceship bitmap to buffer
def spaceship_to_buffer(color):
    buffer = bytearray()
    for row in spaceship_bitmap:
        for pixel in row:
            if pixel == '1':
                buffer.extend(color.to_bytes(2, 'big'))  # Set spaceship color
            else:
                buffer.extend(bg_color.to_bytes(2, 'big'))  # Set background color
    return buffer

# Create the spaceship buffer
spaceship_buffer = spaceship_to_buffer(spaceship_color)
clear_buffer = spaceship_to_buffer(bg_color)  # Buffer for clearing the spaceship

# Function to draw the spaceship using the block function
def draw_spaceship(x, y, clear=False):
    if clear:
        display.block(x, y, x + spaceship_width - 1, y + spaceship_height - 1, clear_buffer)  # Use clear buffer
    else:
        display.block(x, y, x + spaceship_width - 1, y + spaceship_height - 1, spaceship_buffer)  # Use spaceship buffer

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

# Function to display game over message with score and play explosion sound
def display_game_over():
    display.clear(color=color565(255, 255, 255))  # Clear display to black
    draw_large_bitmap(60, 80, game_over_bitmap, color565(0, 0, 0), scale=3)  # Draw the "GAME OVER" bitmap
    display.draw_text8x8(130, 140, f"Score: {score}", color565(0, 0, 0), background = color565(255, 255, 255) )  # White score text
    play_explosion_sound()  # Play explosion sound effect
    sleep_ms(2000)  # Rest for 2 seconds before restarting
    reset_game()

# Function to play explosion sound effect
def play_explosion_sound():
    buzzer.duty_u16(500)  # Turn on buzzer
    for freq in range(2000, 100, -100):  # Rapidly decrease frequency to simulate explosion
        buzzer.freq(freq)
        sleep_ms(10)
    buzzer.duty_u16(0)  # Turn off buzzer

# Function to reset the game
def reset_game():
    global asteroids, score, game_over_flag, game_speed, spaceship_x, melody_index, last_note_time
    asteroids = []  # Clear all asteroids
    score = 0
    game_speed = 1
    game_over_flag = False
    spaceship_x = (320 - spaceship_width) // 2  # Reset spaceship to the center
    melody_index = 0  # Reset melody index
    last_note_time = ticks_ms()  # Reset melody timing
    display.clear(color=bg_color)  # Clear display to black

# Function to display the current score at the top
def display_score():
    display.fill_vrect(0, 0, 320, 16, bg_color)  # Clear previous score area
    display.draw_text8x8(130, 10, f"Score: {score}", score_color,  background = color565(255, 255, 255))  # Display score

# Function to draw an asteroid
def draw_asteroid(x, y, width, height):
    display.fill_vrect(x, y, width, height, asteroid_color)

# Function to clear an asteroid
def clear_asteroid(x, y, width, height):
    display.fill_vrect(x, y, width, height, bg_color)

# Function to play melody based on ticks timing
def play_melody():
    global melody_index, last_note_time
    current_time = ticks_ms()
    if melody_index < len(melody) and ticks_diff(current_time, last_note_time) >= melody[melody_index][1]:
        note, duration = melody[melody_index]
        if note == 0:  # REST note
            buzzer.duty_u16(0)  # Turn off the buzzer
        else:
            buzzer.freq(note)
            buzzer.duty_u16(500)  # Set duty cycle to 500
        melody_index += 1
        last_note_time = current_time
    elif melody_index >= len(melody):
        melody_index = 0  # Loop the melody

# Main game loop
while True:
    # Read potentiometer value to determine steering
    pot_value = pot.read_u16()
    # Calculate the offset from the center position
    offset = pot_value - center_threshold

    # Clear the spaceship at the old position
    draw_spaceship(spaceship_x, spaceship_y, clear=True)

    # Update the spaceship position based on offset, with a deadzone
    if abs(offset) > deadzone:  # Only move if outside the deadzone
        speed = (offset // steering_sensitivity)  # Calculate speed based on offset
        spaceship_x += speed  # Adjust position

    # Keep the spaceship within screen bounds
    if spaceship_x < 0:
        spaceship_x = 0
    elif spaceship_x > 320 - spaceship_width:
        spaceship_x = 320 - spaceship_width

    # Draw the spaceship at the new position
    draw_spaceship(spaceship_x, spaceship_y)

    # Check if it's time to spawn a new asteroid
    current_time = ticks_ms()
    if ticks_diff(current_time, last_asteroid_spawn) > int(asteroid_spawn_interval / game_speed):
        # Spawn a new asteroid at a random x position at the top of the screen with random size
        new_asteroid_x = urandom.randint(0, 320 - 20)
        new_asteroid_width = urandom.randint(8, 20)  # Random width between 8 and 20
        new_asteroid_height = urandom.randint(8, 20)  # Random height between 8 and 20
        asteroids.append((new_asteroid_x, 0, new_asteroid_width, new_asteroid_height))  # Start at the top
        last_asteroid_spawn = current_time

    # Move asteroids down the screen
    for i, (x, y, width, height) in enumerate(asteroids):
        clear_asteroid(x, y, width, height)  # Clear old asteroid position
        new_y = y + int(5 * game_speed)  # Increase speed with game speed
        asteroids[i] = (x, new_y, width, height)  # Update position
        draw_asteroid(x, new_y, width, height)  # Draw new position

        # Check for collision with spaceship
        if new_y + height >= spaceship_y and new_y <= spaceship_y + spaceship_height:
            if x + width >= spaceship_x and x <= spaceship_x + spaceship_width:
                game_over_flag = True

    # Remove off-screen asteroids and increase score
    asteroids = [a for a in asteroids if a[1] < 240]
    score += 1  # Increase score over time
    display_score()  # Update the score display

    # Play melody
    if not game_over_flag:
        play_melody()

    # Check for game over
    if game_over_flag:
        display_game_over()
        continue  # Restart the loop after game over

    # Update game speed gradually
    if score % 50 == 0 and score != 0:  # Increase speed every 50 points
        game_speed += 0.1

    # Reduce sleep time for more responsive movement
    sleep_ms(20)
