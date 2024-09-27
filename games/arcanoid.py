from machine import Pin, SPI, ADC, freq
from utime import sleep_ms  
from libs.ILI9341 import Display, color565

# Set the CPU frequency
freq(270000000)

# Initialize peripherals
pot = ADC(28)
bg_color = color565(0, 0, 0)         # Background color (black)
board_color = color565(255, 255, 255) # Square and paddle color (white)
text_color = color565(255, 255, 255) # Game over text color (white)

# Initialize SPI and Display with corrected pin settings
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(14), cs=Pin(15), rst=Pin(13), width=320, height=240)
display.clear()
# Initialize game variables
def initialize_game():
    global lastPos, posy, posx, dry, drx, ground, top, sideR, sideL, s, paddle_width, paddle_y, game_running
    lastPos = int(pot.read_u16() / 65536 * 240)
    posy, posx = 30, 10
    dry, drx = 1, 1
    ground, top = 230, 30
    sideR, sideL = 300, 10
    s = 0
    paddle_width = 40
    paddle_y = 200
    game_running = True  # Flag to control the game loop
    display.clear()
    score(s)  # Draw initial score

# Function to display score
def score(sc):
    display.fill_vrect(140, 10, 60, 10, bg_color)  # Clear previous score
    display.draw_text8x8(140, 10, f"Score: {sc}", board_color)

# Byte array for "GAME OVER" message in 8x8 bitmap format (scaled up)
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

# Function to display game over block with score
def game_over(final_score):
    # Draw "GAME OVER" bitmap with a scale factor of 3, without a background
    draw_large_bitmap(60, 80, game_over_bitmap, text_color, scale=3)
    # Display the final score below the "GAME OVER" message
    display.fill_vrect(140, 10, 70, 10, bg_color)
    display.draw_text8x8(130, 140, f"Score: {s}", board_color)
    # Rest for 2 seconds after displaying game over
    sleep_ms(2000)
    initialize_game()  # Restart the game after 2 seconds

# Initialize the game
initialize_game()

# Main game loop
while True:  # Continuous loop to allow game restart
    while game_running:  # Use the flag to control the loop
        # Read potentiometer and calculate new paddle position
        pot_value = pot.read_u16()
        posD = 20 + int(pot_value / 273)

        # Clear previous position of the square
        display.fill_vrect(posx, posy, 10, 10, bg_color)  # Erase the square at the old position

        # Update square position with halved speed
        posy += dry * 5
        posx += drx * 5

        # Check if the box hits the ground
        if posy > ground:
            game_over(s)  # Display game over with the final score
            continue  # Restart the game after game over

        # Bounce off top boundaries
        if posy < top:
            dry = -dry
            posy = top  # Ensure it doesn't go beyond
        
        # Bounce off the paddle (if collision is detected)
        if posy + 10 >= paddle_y and posy <= paddle_y + 10:
            if posx + 10 >= posD and posx <= posD + paddle_width:
                dry = -dry
                posy = paddle_y - 10  # Reposition above paddle
                s += 1  # Increment score on successful bounce
                score(s)  # Update score display

        # Bounce off side boundaries
        if posx > sideR:
            drx = -drx
            posx = sideR  # Ensure it doesn't go beyond
        elif posx < sideL:
            drx = -drx
            posx = sideL  # Ensure it doesn't go beyond

        # Draw new position of the square
        display.fill_vrect(posx, posy, 10, 10, board_color)

        # Update paddle position only if it has moved significantly
        if abs(posD - lastPos) > 5:
            display.fill_hrect(lastPos, paddle_y, paddle_width, 10, bg_color)  # Clear previous paddle
            display.fill_hrect(posD, paddle_y, paddle_width, 10, board_color)  # Draw new paddle
            lastPos = posD  # Update last known paddle position

        # Reduce sleep time for more responsive movement
        sleep_ms(20)


