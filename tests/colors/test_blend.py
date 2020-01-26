from repacolors import Color
from repacolors.blend import *


def test_blend():
    r, w = Color("red"), Color("white")

    assert blend(r, w) == r
    assert blend(r.set(alpha=0), w) == w

    r = r.set(alpha=.5)

    assert blend(r, w) == Color("#ffbaba")
    assert blend(r, w, gamma=1) == Color("#ff8080")

    w = w.set(alpha=.5)
    assert blend(r, w, mode="nonexisting") == Color("#ffbaba")
    assert blend(r, w).alpha == .5
    assert blend(r, w).alpha == .5


def test_blend_multiply():
    c1 = Color("#808080")
    c2 = Color("#a08060")
    assert blend(c1, c2, mode="multiply") == Color("#504030")


def test_blend_screen():
    c1 = Color("#808080")
    c2 = Color("#a08060")
    assert blend(c1, c2, mode="screen") == Color("#d0c0b0")


def test_blend_overlay():
    c1 = Color("#808080")
    c2 = Color("#a08060")
    assert blend(c1, c2, mode="overlay") == Color("#a18161")


def test_blend_hardlight():
    c1 = Color("#808080")
    c2 = Color("#a08060")
    assert blend(c1, c2, mode="hard-light") == Color("#a18161")
