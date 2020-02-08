from repacolors import convert, colors, Color
from repacolors.ops import *
import random


def test_normalize_1base():
    for _ in range(100):
        c = convert.RGBTuple(random.random(), random.random(), random.random())
        assert c == normalize_1base(c)

    c = convert.RGBTuple(-1, -1, -1)
    assert normalize_1base(c) == convert.RGBTuple(0, 0, 0)

    c = convert.RGBTuple(1.2, 123, 1.0001)
    assert normalize_1base(c) == convert.RGBTuple(1, 1, 1)


def test_normalize_huebase():
    for _ in range(100):
        c = convert.HSLTuple(random.random(), random.random(), random.random())
        assert c == normalize_huebase(c)

    c = convert.HSLTuple(-1, -1, -1)
    assert normalize_huebase(c) == convert.HSLTuple(0, 0, 0)

    c = convert.HSVTuple(3, 123, 1.0001)
    assert normalize_huebase(c) == convert.HSVTuple(0, 1, 1)

    c = convert.HWBTuple(1.2, .4, .2)
    assert .1999 <= normalize_huebase(c).hue <= .20001


def test_normalize_lab():
    for _ in range(100):
        c = convert.LabTuple(random.random() * 100, random.random() * 256 - 128, random.random() * 256 - 128)
        assert c == normalize_lab(c)

    c = convert.LabTuple(500, 200, 200)
    assert normalize_lab(c) == convert.LabTuple(400, 160, 160)

    c = convert.LabTuple(-200, -200, -200)
    assert normalize_lab(c) == convert.LabTuple(0, -160, -160)


def test_normalize_lch():
    for _ in range(100):
        c = convert.LChTuple(random.random() * 100, random.random() * 200, random.random())
        assert c == normalize_lch(c)

    c = convert.LChTuple(500, 300, .1)
    assert normalize_lch(c) == convert.LChTuple(400, 230, .1)

    c = convert.LChTuple(20, 30, 3.12)
    assert 0.119999 < normalize_lch(c).h < 0.120001


def test_normalize_etc():
    c = (2, 1.5, -3)
    assert c == normalize(c)


def test_get_cspace():
    c = Color("red")

    assert get_cspace(c) == "rgb"
    assert get_cspace(c.rgb) == "rgb"
    assert get_cspace(c.hsl) == "hsl"
    assert get_cspace(c.hsv) == "hsv"
    assert get_cspace(c.hwb) == "hwb"
    assert get_cspace(c.yuv) == "yuv"
    assert get_cspace(c.xyz) == "xyz"
    assert get_cspace(c.lab) == "lab"
    assert get_cspace(c.lch) == "lch"
    assert get_cspace(c.cmyk) == "cmyk"
    assert get_cspace("whatever") == "unknown"


def test_mul_f():
    c = Color(convert.RGBTuple(.1, .1, .1))
    assert mul(c, 3) == Color((.3, .3, .3))


def test_add_hsl():
    c = Color(convert.HSLTuple(.5, .5, .5))
    dct = convert.HSLTuple(.1, .1, .1)
    assert add(c, dct) == Color(convert.HSLTuple(.6, .6, .6))

    c = Color(convert.HSLTuple(.5, .5, .5))
    dc = Color(convert.HSLTuple(.1, .1, .1))
    assert add(c, dc) == Color(convert.HSLTuple(.6, .6, .6))

    c = Color(convert.HSLTuple(.7, .7, .7))
    dct = convert.HSLTuple(-.1, -.1, -.1)
    assert add(c, dct) == Color(convert.HSLTuple(.6, .6, .6))


def test_add_lch():
    c = Color(convert.LChTuple(50, 50, .5))
    dct = convert.LChTuple(10, 10, .1)
    assert add(c, dct) == Color(convert.LChTuple(60, 60, .6))

    c = Color(convert.LChTuple(50, 50, .5))
    dc = Color(convert.LChTuple(10, 10, .1))
    assert add(c, dc) == Color(convert.LChTuple(60, 60, .6))

    c = Color(convert.LChTuple(50, 50, .5))
    dct = convert.LChTuple(-10, -10, -.1)
    assert add(c, dct) == Color(convert.LChTuple(40, 40, .4))


def test_add_lab():
    c = Color(convert.LabTuple(50, 50, -50))
    dct = convert.LabTuple(10, 10, -10)
    assert add(c, dct) == Color(convert.LabTuple(60, 60, -60))

    c = Color(convert.LabTuple(250, 100, -100))
    dc = Color(convert.LabTuple(260, 100, -100))
    assert add(c, dc) == Color(convert.LabTuple(400, 160, -160))


def test_add_rgb():
    c = Color(convert.RGBTuple(.5, .5, .5))
    dct = convert.RGBTuple(.1, .1, .1)
    assert add(c, dct) == Color(convert.RGBTuple(.6, .6, .6))

    c = Color(convert.RGBTuple(.5, .5, .5))
    dc = Color(convert.RGBTuple(.1, .1, .1))
    assert add(c, dc) == Color(convert.RGBTuple(.6, .6, .6))

    c = Color(convert.RGBTuple(.7, .7, .7))
    dct = convert.RGBTuple(-.1, -.1, -.1)
    assert add(c, dct) == Color(convert.RGBTuple(.6, .6, .6))


def test_sub():
    c = Color("#fff")
    dc = Color("#808080")
    assert sub(c, dc) == Color("#7f7f7f")


def test_div():
    c = Color("#c09060")
    dc = 3
    assert div(c, dc) == Color("#403020")


def test_average():
    r, g, b = Color("red"), Color("#0f0"), Color("blue")

    assert average([r, g, b]) == Color("#555")
    assert average([r, g, b], [1, 2, 1]) == Color("#408040")
    assert average([r, g, b], [1, 2, 1], "lch") == Color("#00c336")
    assert average([r, g, b], [1, 2], "lch") == Color("#00c336")
    assert average([r, g, b], [1, 2, 1, 1], "lch") == Color("#00c336")

    assert average([]) == Color()
    assert average([r]) == r
