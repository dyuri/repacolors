from repacolors.convert import *


def eq(rgb1, rgb2):
    h1 = rgb2hex(rgb1, True)
    h2 = rgb2hex(rgb2, True)

    return h1 == h2


def test_ansi_base16():
    for idx, c in enumerate(ANSI16):
        assert eq(c, ansi2rgb(idx))


def test_ansi_out_of_range():
    black = (0, 0, 0)

    assert eq(black, ansi2rgb(-1))
    assert eq(black, ansi2rgb(-45451))
    assert eq(black, ansi2rgb(256))
    assert eq(black, ansi2rgb(1231256))
