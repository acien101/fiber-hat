import time
import esp
import gc
import random
import math

from micropython_dotstar import DotStar
from machine import SPI, Pin

# Shut down Wifi Modem for power consumption
esp.sleep_type(esp.SLEEP_MODEM)

ROWS = 6
COLUMNS = 4
BRIGHTNESS = 0.1
NUM_PIXELS = ROWS * COLUMNS

class Color:
    def __init__(self, r, g, b, brightness = BRIGHTNESS):
        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness

spi = SPI(sck=Pin(14), mosi=Pin(13), miso=Pin(12))
dotstar = DotStar(spi, NUM_PIXELS, auto_write = False, brightness = BRIGHTNESS) # Just one DotStar

RED = Color(255, 0, 0)
GREEN = Color(0,255, 0)
BLUE = Color(0,0,255)
CYAN = Color(0, 125, 125)
YELLOW = Color(125, 125, 0)
PURPLE = Color(125, 0, 125)

def getindex(x, y):
    if x % 2:   # Column 1 and 3
        index = ((x + 1) * ROWS ) - y - 1
    else:       # Column 0 and 2
        index = (x * ROWS) + y
    index = (NUM_PIXELS) - index - 1    # Mirror
    return index

def draw(x, y, color:Color):
    dotstar._set_item(getindex(x,y), [color.r, color.g, color.b, color.brightness])

def drawable(x, y):
    if x > COLUMNS -1 or x < 0:
        return False
    if y > ROWS - 1 or y < 0:
        return False
    return True

def isset(x,y):
    if not drawable(x,y):
        return False
    return dotstar[getindex(x, y)] != (0,0,0)

def vumeter(counter = 10, delay = 0.4):
    """
    Each column with a color and changing like music
    """

    colors = [Color(255, 0, 0, BRIGHTNESS),
              Color(0, 255, 0, BRIGHTNESS),
              Color(0, 0, 255, BRIGHTNESS),
              Color(0, 125, 125, BRIGHTNESS)]

    for i in range(counter):
        dotstar.fill(0)
        for column in range(COLUMNS):
            for j in range(random.randint(0, ROWS - 1)):
                draw(column, ROWS -j - 1, colors[column])
        dotstar.show()
        time.sleep(delay)

def lines(color, delay):
    """
    Horizontal and vertical lines
    """


    for i in range(3):
        random.seed(round(time.time()*1000))
        dotstar.fill(0)
        dotstar.show()

        row = random.randint(0,ROWS - 1)
        for x in range(COLUMNS):
            draw(x, row, color)
            dotstar.show()
            time.sleep(delay)
        column = random.randint(0,COLUMNS - 1)
        for y in range(ROWS):
            draw(column, y, color)
            dotstar.show()
            time.sleep(delay)
    dotstar.fill(0)
    dotstar.show()

class DIRECTION:
    DOWN = 0
    RIGHT = 1
    UP = 2
    LEFT = 3

def spiral(color, initial_x = 0, initial_y = 0, dir = DIRECTION.DOWN):
    delay = 0.1
    c_l = 0 # Counter for lines drawn

    x = initial_x
    y = initial_y

    dotstar.fill(0)
    dotstar.show()
    for i in range(COLUMNS + ROWS):     # Fix this, dont know when finished
        print("-- {} {}".format(x, y))
        while True:
            draw(x, y, color)
            dotstar.show()
            time.sleep(delay)
            if dir == DIRECTION.UP:
                op_x = 0
                op_y = -1
            elif dir == DIRECTION.DOWN:
                op_x = 0
                op_y = 1
            elif dir == DIRECTION.RIGHT:
                op_x = 1
                op_y = 0
            elif dir == DIRECTION.LEFT:
                op_x = -1
                op_y = 0

            if not isset(x + op_x, y + op_y) and drawable(x + op_x, y + op_y):
                x += op_x
                y += op_y
            else:
                break
        dir = dir + 1 if dir < 3 else 0

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b, BRIGHTNESS)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            dotstar[i] = wheel(pixel_index & 255)
        dotstar.show()
        time.sleep(wait)

def color_chase(color:Color, wait):
    for i in range(NUM_PIXELS):
        dotstar[i] = (color.r, color.g, color.b, color.brightness)
        time.sleep(wait)
        dotstar.show()
    time.sleep(0.5)

def color_chase_rev(color:Color, wait):
    for i in reversed(range(NUM_PIXELS)):
        dotstar[i] = (color.r, color.g, color.b, color.brightness)
        time.sleep(wait)
        dotstar.show()
    time.sleep(0.5)

def theaterChase(color:Color, wait):
    dotstar.fill(0)
    dotstar.show()
    for a in range(10):
        for b in range(3):
            dotstar.fill(0)
            c = b
            while c < NUM_PIXELS:
                dotstar[c] = (color.r, color.g, color.b, color.brightness)
                c += 3

            dotstar.show()
            time.sleep(wait)

while True:
    vumeter(counter = 20, delay = 0.4)
    lines(RED, 0.1)
    lines(BLUE, 0.1)
    lines(PURPLE, 0.1)

    spiral(RED)
    spiral(PURPLE, 0, 5, DIRECTION.RIGHT)
    spiral(BLUE, 3, 5, DIRECTION.UP)

    for i in range(5):
        rainbow_cycle(0.001)

    color_chase(RED, 0.1)
    color_chase_rev(BLUE, 0.1)
    color_chase(PURPLE, 0.1)
    color_chase_rev(CYAN, 0.1)

    theaterChase(RED, 0.1)
    theaterChase(BLUE, 0.1)
    theaterChase(PURPLE, 0.1)
    theaterChase(CYAN, 0.1)
