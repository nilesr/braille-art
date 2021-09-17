#!/usr/bin/python3

import argparse
import pathlib
import random

from PIL import Image

###############################################################################
# Functions


def average(x):
    return sum(x) / len(x) if len(x) > 0 else 0


def image_average(image, x1, y1, x2, y2):
    lx = []
    for x in range(x1, x2):
        for y in range(y1, y2):
            lx += [average(base.getpixel((x, y))[:3])]
    return average(lx)


def convert_index(x):
    return {3: 6, 4: 3, 5: 4, 6: 5}.get(x, x)


def match(a, b):
    return a < b if args.invert else a > b


###############################################################################
# Implementation

# Set up argument parser


parser = argparse.ArgumentParser(description='Image to Braille conversion tool')


parser.add_argument('input_file', help='input file to convert', type=pathlib.Path)
parser.add_argument(
    "--invert", help='invert output', dest='invert', action='store_true'
)
parser.add_argument('--dither', '-d', help='dither', type=int, default=10)
parser.add_argument('--sensitivity', '-s', help="sensitivity", type=float, default=0.8)

args = parser.parse_args()
del parser

start = 0x2800
char_width = 10
char_height = char_width * 2
dither = args.dither
sensitivity = args.sensitivity
char_width_divided = round(char_width / 2)
char_height_divided = round(char_height / 4)

base = Image.open(args.input_file)

for y in range(0, base.height - char_height - 1, char_height):
    for x in range(0, base.width - char_width - 1, char_width):
        byte = 0x0
        index = 0
        for xn in range(2):
            for yn in range(4):
                avg = image_average(base,
                                    x + (char_height_divided * xn),
                                    y + (char_width_divided * yn),
                                    x + (char_height_divided * (xn + 1)),
                                    y + (char_width_divided * (yn + 1)))

                if match(avg + random.randint(-dither, dither), sensitivity * 0xFF):
                    byte += 2**convert_index(index)
                index += 1
        print(chr(start + byte), end="")
    print()
