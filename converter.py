# simply drag and drop an image onto this python file.
# 'python converter.py image.png' for terminal user.

import os
import sys
import cv2
import math

from colorama import init
init()


def map(x: float, in_min: float, in_max: float, out_min: float, out_max: float):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def image_resize(image: cv2.Mat, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # ratio for the text size and line spacing
    height_to_width_ratio = 18/10
    width_to_height_ratio = 10/18

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height * height_to_width_ratio / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width * width_to_height_ratio / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def resize_based_on_terminal_size(image: cv2.Mat):
    columns, lines = os.get_terminal_size()
    image_height_constraint = image_resize(image, height=lines)
    image_width_constraint = image_resize(image, width=columns)
    if image_height_constraint.shape[1] < columns:
        return image_height_constraint
    else:
        return image_width_constraint


def image_to_ascii(image: cv2.Mat):
    ascii_palette = '   ...\',;:clodxkO0KXNWM'
    text = ''
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for row in gray:
        for pixel in row:
            palette_index = round(map(pixel, 0, 255, 0, 23))
            text += ascii_palette[palette_index]
        text += '\n'
    return text[:-1]


def color_distance(color1, color2):
    rmean = 0.5*(color1[0]+color2[0])
    dist = sum((2+rmean, 4, 3-rmean)*(color1-color2)**2)**0.5
    return dist


def ascii_to_color(image: cv2.Mat, text: str):
    RESET = '\033[0m'
    COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
            'strong_grey',
            'strong_red',
            'strong_green',
            'strong_yellow',
            'strong_blue',
            'strong_magenta',
            'strong_cyan',
            'strong_white',
        ],
            list(range(30, 38))
            + list(range(90, 98))
        ))
    )

    color_map = {
        'grey': [12, 12, 12],
        'red': [197, 15, 31],
        'green': [19, 161, 14],
        'yellow': [193, 156, 0],
        'blue': [0, 55, 218],
        'magenta': [136, 23, 152],
        'cyan': [58, 150, 221],
        'white': [204, 204, 204],
        'strong_grey': [118, 118, 118],
        'strong_red': [231, 72, 86],
        'strong_green': [22, 198, 12],
        'strong_yellow': [249, 241, 165],
        'strong_blue': [59, 120, 255],
        'strong_magenta': [180, 0, 158],
        'strong_cyan': [97, 214, 214],
        'strong_white': [242, 242, 242],
    }

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    fmt_str = '\033[%dm'
    new_text = ''
    for row, lines in zip(image_rgb, text.splitlines()):
        previous_color = ''
        for pixel, letter in zip(row, lines):
            best_color = 'grey'
            best_dist = math.inf
            for color, value in color_map.items():
                if (dist := color_distance(pixel, value)) < best_dist:
                    best_color = color
                    best_dist = dist
            if previous_color != best_color:
                if previous_color:
                    new_text += RESET
                new_text += fmt_str % (COLORS[best_color])
                previous_color = best_color
            new_text += letter
        new_text += '\n'
    return new_text[:-1] + RESET


for arg in sys.argv[1:]:
    os.system('pause')
    image = cv2.imread(arg)
    image = resize_based_on_terminal_size(image)
    text = image_to_ascii(image)
    text = ascii_to_color(image, text)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(text)
    os.system('pause')
