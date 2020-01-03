from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_hsl_dedicated_greys():
    colors = [
        ((1, 1, 1), (0, 0, 1)),  # white - red
        ((0, 0, 0), (.3333, 0, 0)),  # black - green
        ((.5, .5, .5), (.6667, 0, .5)),  # grey - blue
    ]

    for rgb, hsl in colors:
        assert eq(hsl2rgb(hsl), rgb)


def test_hsl_dedicated_nongreys():
    colors = [
        ((0, 1, 0), (.3333, 1, .5)),  # green
        ((0, 0, 1), (.6667, 1, .5)),  # blue
        ((1, 1, 0), (.1667, 1, .5)),  # yellow
        ((1, 0, 1), (.8333, 1, .5)),  # magenta
        ((0, 1, 1), (.5, 1, .5)),  # cyan
    ]

    for rgb, hsl in colors:
        assert eq(hsl2rgb(hsl), rgb)


def test_hsl_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = hsl2rgb(rgb2hsl(c))
        assert eq(c, c2)
