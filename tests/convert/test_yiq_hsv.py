from repacolors.convert import *
import random


def test_yiq_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = yiq2rgb(rgb2yiq(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005


def test_hsv_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        c2 = hsv2rgb(rgb2hsv(c))
        assert abs(c.red - c2.red) < 0.005
        assert abs(c.green - c2.green) < 0.005
        assert abs(c.blue - c2.blue) < 0.005
