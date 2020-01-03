from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_lab_dedicated():
    colors = [
        ((1, 1, 1), (100, .00526, -.0104)),  # white
        ((0, 0, 0), (0, 0, 0)),  # black
        ((.5, .5, .5), (53.3889, .0031, -.0062)),  # grey
        ((1, 0, 0), (53.2328, 80.1093, 67.22)),  # red
        ((0, 1, 0), (87.737, -86.1846, 83.1812)),  # green
        ((0, 0, 1), (32.3026, 79.1967, -107.8637)),  # blue
        ((1, 1, 0), (97.1382, -21.5559, 94.4825)),  # yellow
        ((1, 0, 1), (60.3199, 98.2542, -60.843)),  # magenta
        ((0, 1, 1), (91.1165, -48.0796, -14.1381)),  # cyan
    ]

    for rgb, lab in colors:
        assert eq(lab2rgb(lab), rgb)


def test_lab_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = lab2rgb(rgb2lab(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
