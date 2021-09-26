#!/usr/bin/python3

import argparse
import pathlib
import random
import re

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
parser = argparse.ArgumentParser(
    description='Image to Braille conversion tool')

parser.add_argument(
    'input_file', help='input file to convert', type=pathlib.Path)
parser.add_argument(
    "--invert", help='invert output', dest='invert', action='store_true')
parser.add_argument('--dither', '-d', help='dither', type=int, default=10)
parser.add_argument(
    '--sensitivity', '-s', help="sensitivity", type=float, default=0.8)
parser.add_argument(
    '--char_width', '-c', help="character width", type=int, default=10)
parser.add_argument('-i', '--iterative', help="iteratively change a parameter",
                    dest='iterative', action='store_true')

args = parser.parse_args()
del parser

start = 0x2800
char_width = args.char_width
char_height = char_width * 2

# dither = args.dither
# sensitivity = args.sensitivity

char_width_divided = round(char_width / 2)
char_height_divided = round(char_height / 4)

base = Image.open(args.input_file)


def print_image(_sensitivity, _dither):
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
                    if match(avg + random.randint(-_dither, _dither),
                             _sensitivity * 0xFF):
                        byte += 2**convert_index(index)
                    index += 1
            print(chr(start + byte), end="")
        print()


class Param:
    stor = {
        'd': args.dither,
        'db': (1, 100),  # bounds
        's': args.sensitivity,
        'sb': (0.0, 1.0),  # bounds
    }

    def __getitem__(self, key):
        return self.stor[key]

    def __setitem__(self, key, value):
        if isinstance(type(value), type(self.stor[key])):
            raise ValueError("value {} for key {} is not of the same type, \
            expected ".format(value, key))
        else:
            b = key+'b'
            if value <= self.stor[b][0]:
                self.stor[key] = self.stor[b][0]
                print("lower bound {} of param {} reached"
                      .format(self.stor[b][0], key))
            elif value >= self.stor[b][1]:
                self.stor[key] = self.stor[b][1]
                print("upper bound {} of param {} reached"
                      .format(self.stor[b][1], key))
            else:
                self.stor[key] = value

    def help(self):
        print('use d to change dither, s to change sensitivity')


param = Param()
patt = re.compile(r"[a-z][ ]*[s+\-][ ]*\d+([.]{0,1})\d*")

while 1:
    print_image(param['s'], param['d'])

    if (args.iterative):
        _res = input("type a parameter name, and how much to change: ")
        res = _res.strip()  # if _res != 'r' else res
        # TODO: make some way to iteratively repeat adjustments
        print("input", res)
        cmd = res[0]
        # print("cmd:", cmd)

        if patt.match(res):
            d = res[1]
            num = res[2:]
            print(cmd, d, num)
            try:
                try:
                    if d == '+':
                        param[cmd] += type(param[cmd])(num)
                    elif d == '-':
                        param[cmd] -= type(param[cmd])(num)
                    elif d == 's':
                        param[cmd] = type(param[cmd])(num)
                except ValueError:
                    print("invalid input number")
            except KeyError:
                print("Invalid number: {}".format(num))
        else:
            if cmd == 'q':
                print("exitting.")
                break
            elif cmd == 'h':
                print("commands:")
                param.help()
            else:
                try:
                    print("param: {} - {}".format(cmd, param[cmd]))
                except KeyError:
                    print("""invalid input {}, expected in the form a+10.0 or a
                single letter, send h for help, q to quit""".format(res))
    else:
        break
