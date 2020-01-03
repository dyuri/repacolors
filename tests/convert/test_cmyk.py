from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_cmyk_dedicated():
    colors = [
        ((1, 1, 1), (0, 0, 0, 0)),  # white
        ((0, 0, 0), (0, 0, 0, 1)),  # black
        ((.5, .5, .5), (0, 0, 0, .5)),  # grey
        ((1, 0, 0), (0, 1, 1, 0)),  # red
        ((0, 1, 0), (1, 0, 1, 0)),  # green
        ((0, 0, 1), (1, 1, 0, 0)),  # blue
        ((1, 1, 0), (0, 0, 1, 0)),  # yellow
        ((1, 0, 1), (0, 1, 0, 0)),  # magenta
        ((0, 1, 1), (1, 0, 0, 0)),  # cyan
    ]

    for rgb, cmyk in colors:
        assert eq(cmyk2rgb(cmyk), rgb)


def test_cmyk_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = cmyk2rgb(rgb2cmyk(c))
        assert eq(c, c2)
