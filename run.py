from PIL import Image
import random, sys

import pathlib
import argparse as ap

# Set up argument parser
parser = ap.ArgumentParser(description='Image to Braille conversion tool')
parser.add_argument('input_file',
                    help='input file to convert',
                    type=pathlib.Path)
                    #type=ap.FileType('r'))

args = parser.parse_args();
del parser

average = lambda x: sum(x)/len(x) if len(x) > 0 else 0
start = 0x2800
char_width = 10
char_height = char_width * 2
dither = 10
sensitivity = 0.8
char_width_divided = round(char_width / 2)
char_height_divided = round(char_height / 4)

#filename = "../Pictures/Anthony Foxx official portrait.jpg"
#filename = "../Pictures/bait k.jpg"
#filename = "sample.png"

#args.input_file.close()

base = Image.open(args.input_file)
match = lambda a, b: a < b if "--invert" in sys.argv else a > b
def image_average(x1, y1, x2, y2):
    return average([average(base.getpixel((x, y))[:3]) for x in range(x1, x2) for y in range(y1, y2)])
def convert_index(x):
    return {3: 6, 4: 3, 5: 4, 6: 5}.get(x, x)
for y in range(0, base.height - char_height - 1, char_height):
    for x in range(0, base.width - char_width - 1, char_width):
        byte = 0x0
        index = 0
        for xn in range(2):
            for yn in range(4):
                avg = image_average(x + (char_height_divided * xn), y + (char_width_divided * yn), x + (char_height_divided * (xn + 1)), y + (char_width_divided * (yn + 1)))
                if match(avg + random.randint(-dither, dither), sensitivity * 0xFF):
                    byte += 2**convert_index(index)
                index += 1
        print(chr(start + byte), end = "")
    print()
