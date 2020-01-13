from repacolors import convert, colors, Color
import random


def test_normalize_rgb():
    for _ in range(100):
        c = convert.RGBTuple(random.random(), random.random(), random.random())
        assert c == colors.normalize_rgb(c)

    c = convert.RGBTuple(-1, -1, -1)
    assert colors.normalize_rgb(c) == convert.RGBTuple(0, 0, 0)

    c = convert.RGBTuple(1.2, 123, 1.0001)
    assert colors.normalize_rgb(c) == convert.RGBTuple(1, 1, 1)


def test_normalize_hsl():
    for _ in range(100):
        c = convert.HSLTuple(random.random(), random.random(), random.random())
        assert c == colors.normalize_hsl(c)

    c = convert.HSLTuple(-1, -1, -1)
    assert colors.normalize_hsl(c) == convert.RGBTuple(0, 0, 0)

    c = convert.HSLTuple(3, 123, 1.0001)
    assert colors.normalize_hsl(c) == convert.RGBTuple(0, 1, 1)

    c = convert.HSLTuple(1.2, 1, 1)
    assert .1999 <= colors.normalize_hsl(c).hue <= .20001


def test_mul():
    c = convert.RGBTuple(.1, .1, .1)
    assert Color(colors.mul(c, 3)) == Color((.3, .3, .3))

    c = convert.RGBTuple(.6, .6, .6)
    assert Color(colors.mul(c, .5)) == Color((.3, .3, .3))


def test_add_hsl():
    c = Color(convert.HSLTuple(.5, .5, .5))
    dct = convert.HSLTuple(.1, .1, .1)
    assert colors.add_hsl(c, dct) == Color(convert.HSLTuple(.6, .6, .6))

    c = Color(convert.HSLTuple(.5, .5, .5))
    dc = Color(convert.HSLTuple(.1, .1, .1))
    assert colors.add_hsl(c, dc) == Color(convert.HSLTuple(.6, .6, .6))

    c = Color(convert.HSLTuple(.7, .7, .7))
    dct = convert.HSLTuple(-.1, -.1, -.1)
    assert colors.add_hsl(c, dct) == Color(convert.HSLTuple(.6, .6, .6))


def test_add_rgb():
    c = Color(convert.RGBTuple(.5, .5, .5))
    dct = convert.RGBTuple(.1, .1, .1)
    assert colors.add_rgb(c, dct) == Color(convert.RGBTuple(.6, .6, .6))

    c = Color(convert.RGBTuple(.5, .5, .5))
    dc = Color(convert.RGBTuple(.1, .1, .1))
    assert colors.add_rgb(c, dc) == Color(convert.RGBTuple(.6, .6, .6))

    c = Color(convert.RGBTuple(.7, .7, .7))
    dct = convert.RGBTuple(-.1, -.1, -.1)
    assert colors.add_rgb(c, dct) == Color(convert.RGBTuple(.6, .6, .6))

