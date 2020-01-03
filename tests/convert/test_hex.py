from repacolors.convert import *
import random
import pytest


def test_hex_long_short():
    c = RGBTuple(1, 1, 1)  # white
    assert rgb2hex(c) == '#fff'
    assert rgb2hex(c, False) == '#fff'
    assert rgb2hex(c, True) == '#ffffff'

    c = RGBTuple(0, 0, 0)  # black
    assert rgb2hex(c) == '#000'
    assert rgb2hex(c, False) == '#000'
    assert rgb2hex(c, True) == '#000000'

    c = RGBTuple(1, 2/3, 0)  # ~orange
    assert rgb2hex(c) == '#fa0'
    assert rgb2hex(c, False) == '#fa0'
    assert rgb2hex(c, True) == '#ffaa00'

    c = RGBTuple(1, 0.647, 0)  # "orange"
    assert rgb2hex(c) == '#ffa500'
    assert rgb2hex(c, False) == '#ffa500'
    assert rgb2hex(c, True) == '#ffa500'


def test_hex_reverse():
    for _ in range(100):
        c = RGBTuple(random.random(), random.random(), random.random())
        hx = rgb2hex(c)
        c2 = hex2rgb(hx)
        assert c.red - c2.red < 0.005
        assert c.green - c2.green < 0.005
        assert c.blue - c2.blue < 0.005
        assert hx == rgb2hex(c2)


def test_hex_invalid():
    with pytest.raises(ValueError):
        hex2rgb("whatever")
