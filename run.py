from PIL import Image
import random, sys
average = lambda x: sum(x)/len(x) if len(x) > 0 else 0
start = 0x2800
char_width = 10
char_height = char_width * 2
dither = 20
sensitivity = 0.4
char_width_divided = round(char_width / 2)
char_height_divided = round(char_height / 4)
filename = "../Pictures/Anthony Foxx official portrait.jpg"
#filename = "../Pictures/anime pepe.png"
base = Image.open(filename)
match = lambda a, b: a < b if "--invert" in sys.argv else a > b
def image_average(x1, y1, x2, y2):
    ret = []
    for x in range(x1, x2):
        for y in range(y1, y2):
            ret.append(average(base.getpixel((x, y))[:3]))
    return average(ret)
def convert_index(x):
    if x < 3: return x
    if x == 3: return 6
    if x == 4: return 3
    if x == 5: return 4
    if x == 6: return 5
    if x == 7: return 7
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
