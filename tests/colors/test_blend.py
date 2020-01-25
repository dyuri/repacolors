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
    assert blend(r, w) == Color("#ffbaba")
    assert blend(r, w).alpha == .5
