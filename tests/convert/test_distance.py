from repacolors.convert import *
import random


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_distance_same():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        assert distance(c, c) == 0


def test_distance_not_same():
    for _ in range(100):
        c1 = RGBTuple(random.random(), random.random(), random.random())
        c2 = RGBTuple(random.random(), random.random(), random.random())
        if c1 != c2:
            assert distance(c1, c2) > 0


def test_distance_triangle():
    for _ in range(100):
        c1 = RGBTuple(random.random(), random.random(), random.random())
        c2 = RGBTuple(random.random(), random.random(), random.random())
        c3 = RGBTuple(random.random(), random.random(), random.random())
        d12 = distance(c1, c2)
        d23 = distance(c2, c3)
        d13 = distance(c1, c3)

        assert d12 + d23 >= d13