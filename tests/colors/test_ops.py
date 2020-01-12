from repacolors import convert, colors, Color


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

