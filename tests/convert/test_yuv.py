from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_yuv_dedicated():
    colors = [
        ((1, 1, 1), (1, 0, 0)),  # white
        ((0, 0, 0), (0, 0, 0)),  # black
        ((.5, .5, .5), (.5, 0, 0)),  # grey
        ((1, 0, 0), (.3, -.1687, .5)),  # red
        ((0, 1, 0), (.587, -.3313, -.4186)),  # green
        ((0, 0, 1), (.114, .5, -.0813)),  # blue
        ((1, 1, 0), (.886, -.5, .0813)),  # yellow
        ((1, 0, 1), (.413, .3312, .4186)),  # magenta
        ((0, 1, 1), (.701, .1686, -.5)),  # cyan
    ]

    for rgb, yuv in colors:
        assert eq(yuv2rgb(yuv), rgb)


def test_yuv_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = yuv2rgb(rgb2yuv(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
