from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_lab_dedicated():
    colors = [
        ((1, 1, 1), (100, .012, 296.813 / 360)),  # white
        ((0, 0, 0), (0, 0, 0)),  # black
        ((.5, .5, .5), (53.3889, .007, 296.813 / 360)),  # grey
        ((1, 0, 0), (53.2328, 104.576, 40 / 360)),  # red
        ((0, 1, 0), (87.737, 119.778, 136.01592 / 360)),  # green
        ((0, 0, 1), (32.3026, 133.816, 306.287 / 360)),  # blue
        ((1, 1, 0), (97.1382, 96.91, 102.8516 / 360)),  # yellow
        ((1, 0, 1), (60.3199, 115.567, 328.233 / 360)),  # magenta
        ((0, 1, 1), (91.1165, 50.115, 196.386 / 360)),  # cyan
    ]

    for rgb, lch in colors:
        assert eq(lch2rgb(lch), rgb)


def test_lch_reverse():
    for _ in range(100):
        wp = random.choice([D50, D55, D65, D75])
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = lch2rgb(rgb2lch(c, wp), wp)
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
