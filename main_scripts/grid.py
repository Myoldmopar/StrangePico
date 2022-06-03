from machine import Pin
from neopixel import NeoPixel
from time import sleep

# some global variables common to the overall script operation, don't modify
num_pins = 64
np = NeoPixel(Pin(16), num_pins)
scene = []
cel_index = 0

# 16 available colors, based on the EGA default palette here:
# https://en.wikipedia.org/wiki/Enhanced_Graphics_Adapter#Color_palette 
colors = {
    "-": (00, 00, 00),  # off
    "0": (00, 00, 00),  # black
    "1": (00, 00, 15),  # blue
    "2": (00, 15, 00),  # green
    "3": (00, 15, 15),  # cyan
    "4": (15, 00, 00),  # red
    "5": (15, 00, 15),  # magenta
    "6": (15, 08, 00),  # brown
    "7": (15, 15, 15),  # light gray
    "8": (08, 08, 08),  # dark gray
    "9": (08, 08, 15),  # bright blue
    "A": (08, 15, 08),  # bright green
    "B": (08, 15, 15),  # bright cyan
    "C": (15, 08, 08),  # bright red
    "D": (15, 08, 15),  # bright magenta
    "E": (15, 15, 08),  # bright yellow
    "F": (15, 15, 15),  # bright white
    }

# ********** BEGIN DEFINING INDIVIDUAL CELS ********** #

# Cels should be 8 rows of 8 characters each
# You can copy the 'base' one here to start with
# Then as you animate, just copy, rename, and modify

base = [
    #01234567####
    "--------",#0
    "--------",#1
    "--------",#2
    "--------",#3
    "--------",#4
    "--------",#5
    "--------",#6
    "--------"]#7

test = [
    #01234567####
    "01234567",#0
    "01234567",#1
    "01234567",#2
    "01234567",#3
    "89ABCDEF",#4
    "89ABCDEF",#5
    "89ABCDEF",#6
    "89ABCDEF"]#7

hi = [
    #01234567####
    "1---1---",#0
    "2---2-A-",#1
    "3---3---",#2
    "44444-B-",#3
    "5---5-C-",#4
    "6---6-D-",#5
    "7---7-E-",#6
    "8---8-F-"]#7

mario_1 = [
    #01234567####
    "--444---",#0
    "--44444-",#1
    "--6-6---",#2
    "--66-6--",#3
    "-11C1C--",#4
    "1-16461-",#5
    "--4444--",#6
    "--1--1--"]#7

mario_2 = [
    #01234567####
    "--444---",#0
    "--44444-",#1
    "--6-6---",#2
    "--6666--",#3
    "-11C1C--",#4
    "-116441-",#5
    "--4444--",#6
    "---1-1--"]#7

# ********** END DEFINING INDIVIDUAL CELS ********** #

# ********** BEGIN PROGRAM OPERATION: DONT MODIFY ********** #

def make(visual: list) -> str:
    global cel_index, colors
    # check the cel grid to verify it has 8 rows first
    if len(visual) != 8:
        cel = "\n".join([f"\"{row}\"" for row in visual])
        raise Exception(f"Invalid number of rows in cel #{cel_index}, must be an 8x8 grid of characters.  Cel contents: \n{cel}")
    # then check each row to make sure it has 8 characters in it
    if any([len(row) != 8 for row in visual]):
        cel = ""
        for this_row in visual:
            if len(this_row) == 8:
                cel += f"\"{this_row}\"\n"
            else:
                cel += f"\"{this_row}\" << invalid row\n"
        raise Exception(f"Invalid number of columns in a row in cel #{cel_index}, must be an 8x8 grid of characters.  Cel contents: \n{cel}")        
    # now generator the actual color list
    out = []
    going_up = True
    avail_keys = "".join(sorted(colors.keys()))
    for col in range(7, -1, -1):
        if going_up:
            for row in range(7, -1, -1):
                this_color_code = visual[row][col]
                if this_color_code not in colors:
                    raise Exception(f"Bad character in cel #{cel_index}: \"{this_color_code}\", available characters are: \"{avail_keys}\"")
                out.append(colors[this_color_code])
        else:
            for row in range(8):
                this_color_code = visual[row][col]
                if this_color_code not in colors:
                    raise Exception(f"Bad character in cel #{cel_index}: \"{this_color_code}\", available characters are: \"{avail_keys}\"")
                out.append(colors[this_color_code])
        going_up = not going_up
    return out


def add_cel(raw_cel: list, animation_seconds: float) -> None:
    global cel_index, scene
    cel_index += 1
    scene.append((make(raw_cel), animation_seconds))
    

def run_scene() -> None:
    global scene, num_pins
    while True:
        for cel in scene:
            for x in range(num_pins):
                np[x] = cel[0][x]
            np.write()
            sleep(cel[1])
        sleep(1)


# ********** END PROGRAM OPERATION ********** #

# ********** BEGIN DEFINING ANIMATION ********** #

# You need to specify how the individual cels should be shown
# Just call 'add_cel function, and pass your raw cel as you named it above
# Along with how many seconds you want that cel to be shown.  The seconds
# can be decimal, like 0.1 or 1.5

# If you create a cel incorrectly, like it's not 8x8 shaped, you will get
# an error message saying "problem with cel # whatever.  That # is simply
# the order you added it in this list of add_cel function calls.

add_cel(test, 1)
add_cel(hi, 1)
add_cel(mario_1, 0.7)
add_cel(mario_2, 0.7)
add_cel(mario_1, 0.7)
add_cel(mario_2, 0.7)

# ********** END DEFINING ANIMATION ********** #

run_scene()  # then this will just call the function to actually run the scene and loop over it forever
