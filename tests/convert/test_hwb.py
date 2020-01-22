from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_hwb_dedicated():
    colors = [
        ((1, 1, 1), (0, 1, 0)),  # white
        ((0, 0, 0), (0, 0, 1)),  # black
        ((.5, .5, .5), (0, .5, .5)),  # grey
        ((1, 0, 0), (0, 0, 0)),  # red
        ((0, 1, 0), (.3333333, 0, 0)),  # green
        ((0, 0, 1), (.6666667, 0, 0)),  # blue
        ((1, 1, 0), (.1666667, 0, 0)),  # yellow
        ((1, 0, 1), (.8333333, 0, 0)),  # magenta
        ((0, 1, 1), (.5, 0, 0)),  # cyan
    ]

    for rgb, hwb in colors:
        assert eq(hwb2rgb(hwb), rgb)


def test_lab_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = hwb2rgb(rgb2hwb(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
