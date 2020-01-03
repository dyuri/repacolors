from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_xyz_dedicated():
    colors = [
        ((1, 1, 1), (.9505, 1.0, 1.089)),  # white
        ((0, 0, 0), (0, 0, 0)),  # black
        ((.5, .5, .5), (.2034, .214, .2331)),  # grey
        ((1, 0, 0), (.4124, .2126, .0193)),  # red
        ((0, 1, 0), (.3576, .7152, .1192)),  # green
        ((0, 0, 1), (.1805, .0722, .9505)),  # blue
        ((1, 1, 0), (.77, .9278, .1385)),  # yellow
        ((1, 0, 1), (.5929, .2848, .9698)),  # magenta
        ((0, 1, 1), (.5381, .7874, 1.0697)),  # cyan
    ]

    for rgb, xyz in colors:
        assert eq(xyz2rgb(xyz), rgb)


def test_xyz_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = xyz2rgb(rgb2xyz(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
