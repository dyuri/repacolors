from repacolors import Color, colors, convert, ops
import pytest
import io
import random


def about_the_same(x, y, epsilon=0.001):
    return x - epsilon < y < x + epsilon


def test_create_from_colortuple():
    rgb = convert.RGBTuple(1, 0, 0)  # red
    c = Color(rgb)
    assert rgb == c.rgb
    assert c.lhex == "#ff0000"

    hsl = convert.HSLTuple(0, 1, .5)  # red
    c = Color(hsl)
    assert hsl == c.hsl
    assert c.lhex == "#ff0000"

    lab = convert.LabTuple(53.23288, 80.1093, 67.22)  # red
    c = Color(lab)
    assert lab == c.lab
    assert c.lhex == "#ff0000"

    lch = convert.LChTuple(53.23288, 104.5755, 0.1111)  # red
    c = Color(lch)
    assert lch == c.lch
    assert c.lhex == "#ff0000"

    xyz = convert.XYZTuple(.4124, .2126, .0193)  # red
    c = Color(xyz)
    assert xyz == c.xyz
    assert c.lhex == "#ff0000"

    yuv = convert.YUVTuple(.299, -.168736, .5)  # red
    c = Color(yuv)
    assert yuv == c.yuv
    assert c.lhex == "#ff0000"

    cmyk = convert.CMYKTuple(0, 1, 1, 0)  # red
    c = Color(cmyk)
    assert cmyk == c.cmyk
    assert c.lhex == "#ff0000"

    rgbt = (1, 0, 0)
    c = Color(rgbt)
    assert rgbt == c.rgb
    assert c.lhex == "#ff0000"

    rgb256t = (255, 0, 0)
    c = Color(rgb256t)
    assert rgb256t == c.rgb256
    assert c.lhex == "#ff0000"

    rgbt = (1, 0, 0, .25)
    c = Color(rgbt)
    assert rgbt[:3] == c.rgb
    assert c.lhex == "#ff0000"
    assert c.alpha == .25

    rgb256t = (255, 0, 0, 128)
    c = Color(rgb256t)
    assert rgb256t[:3] == c.rgb256
    assert c.lhex == "#ff0000"
    assert c.alpha - .5 < 0.01


def test_create_from_color():
    c1 = Color((1, 0, 0))
    c2 = Color(c1)
    assert c1 is not c2
    assert c1 == c2
    assert c1.hsl == c2.hsl


def test_create_from_bytes():
    c = Color(b'\xff\x00\x00')
    assert c.lhex == "#ff0000"
    assert c.alpha == 1

    c = Color(b'\xff\x00\x00\x00')
    assert c.lhex == "#ff0000"
    assert c.alpha == 0


def test_create_from_str():
    c = Color("#f00")
    assert c.lhex == "#ff0000"

    c = Color("#ff0000")
    assert c.lhex == "#ff0000"

    c = Color("#f00a")
    assert c.lhex == "#ff0000"
    assert c.alpha - .66667 < 0.00001

    c = Color("#ff000080")
    assert c.lhex == "#ff0000"
    assert 0.49 < c.alpha < 0.51

    c = Color("red")
    assert c.lhex == "#ff0000"

    # whatever, from hash
    c = Color("whatever")
    assert isinstance(c, Color)


def test_create_from_cssrgb():
    cdefs = [
        "rgb(255,0,153)",
        "rgb(255, 0, 153)",
        "rgba(255, 0, 153.0)",
        "rgb(100%,0%,60%)",
        "rgb(100%, 0%, 60%)",
        "rgba(100%, 0, 60%)",
        "rgb(255 0 153)",
        "rgb(255, 0, 153, 1)",
        "rgb(255, 0, 153, 100%)",
        "rgba(255 0 153 / 1)",
        "rgb(255 0 153 / 100%)",
        "rgb(255, 0, 152.99, 1)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#ff0099ff"

    cdefs = [
        "rgba(255,0,153,.5)",
        "rgb(255, 0, 153,50%)",
        "rgba(255 0 153.0 /  .5)",
        "rgb(255 0% 153 /  50%)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#ff00997f"


def test_create_from_csshsl():
    cdefs = [
        "hsl(270,60%,70%)",
        "hsla(270, 60%, 70%, 100%)",
        "hsl(270 60% 70%)",
        "hsla(270deg, 60%, 70%, 1)",
        "hsl(4.71239rad, 60%, 70%)",
        "hsl(.75turn, 60%, 70%)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#b385e1ff"

    cdefs = [
        "hsl(270, 60%, 50%, .15)",
        "hsla(270, 60%, 50%, 15%)",
        "hsl(270 60% 50% / .15)",
        "hsla(270 60% 50% / 15%)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#8033cc26"


def test_create_from_csshwb():
    cdefs = [
        "hwb(270,60%,70%)",
        "hwb(270, 60%, 70%, 100%)",
        "hwb(270 60% 70%)",
        "hwb(270deg, 60%, 70%, 1)",
        "hwb(4.71239rad, 60%, 70%)",
        "hwb(.75turn, 60%, 70%)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#73994dff"

    cdefs = [
        "hwb(270, 60%, 50%, .15)",
        "hwb(270, 60%, 50%, 15%)",
        "hwb(270 60% 50% / .15)",
        "hwb(270 60% 50% / 15%)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#8c998026"


def test_create_from_csslab():
    cdefs = [
        "lab(58.93% -26.61 35.55)",
        "lab(58.93, -26.61, 35.55)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#73994dff"

    cdefs = [
        "lab(61.58 -9.4 11.59 / 0.14902)",
        "lab(61.58%, -9.4, 11.59, 0.14902)",
    ]

    for cdef in cdefs:
        c = Color(cdef)
        assert c.lhexa == "#8c998026"


def test_create_from_cssgray():
    assert Color("gray(50)") == Color(convert.LabTuple(50, 0, 0))
    assert Color("gray(75 / .5)") == Color(convert.LabTuple(75, 0, 0), .5)
    assert Color("gray(  25  /   .50 )") == Color(convert.LabTuple(25, 0, 0), .5)


def test_create_with_extra_params():
    c = Color(rgb=(1, 0, 0), alpha=.5)
    assert c.lhex == "#ff0000"
    assert c.alpha == .5

    c = Color(red=1, green=0, blue=0, alpha=0)
    assert c.lhex == "#ff0000"
    assert c.alpha == 0

    c = Color(r=0, g=255, b=255)
    assert c.lhex == "#00ffff"

    c = Color(hue=0, saturation=1, lightness=.5)
    assert c.lhex == "#ff0000"

    c = Color(cie_l=53.23288, cie_a=80.1093, cie_b=67.22)
    assert c.lhex == "#ff0000"

    c = Color(cie_x=.4124, cie_y=.2126, cie_z=.0193)
    assert c.lhex == "#ff0000"

    c = Color(y=.299, u=-.168736, v=.5)
    assert c.lhex == "#ff0000"

    c = Color(hex="#ff0000")
    assert c.lhex == "#ff0000"

    # red -> blue
    c = Color("blue", hue=0)
    assert c.lhex == "#ff0000"


def test_equality():
    c1 = Color("red", equality=ops.equal_hex)
    c2 = Color("#ff0000", equality=ops.equal_hex)
    assert c1 == c2

    c1 = Color("red", equality=ops.equal_hsl)
    c2 = Color("#ff0000", equality=ops.equal_hsl)
    assert c1 == c2

    c1 = Color("red", equality=ops.equal_hsla)
    c2 = Color("#ff0000", equality=ops.equal_hsla)
    assert c1 == c2

    c1 = Color("red", equality=ops.equal_hash)
    c2 = Color("#ff0000", equality=ops.equal_hash)
    assert c1 == c2


def test_equality_negative():
    c1 = Color("#ff0000")
    c2 = Color("#ff0001")
    assert c1 != c2
    assert c1 != "#ff0000"  # not compatible type

    c1 = Color("black", equality=ops.equal_hsl, hue=.6666)
    c2 = Color("black", equality=ops.equal_hex, hue=0)
    assert c2 == c1
    assert c1 != c2

    c1 = Color("red", equality=ops.equal_hsl, alpha=.5)
    c2 = Color("red", equality=ops.equal_hsla, alpha=1)
    assert c1 == c2
    assert c2 != c1

    c1 = Color("cyan", equality=ops.equal_hsl, hue=.501)
    c2 = Color("cyan", equality=ops.equal_hash)
    print(repr(c1), repr(c2))
    print(hash(c1), hash(c2))
    assert c1 == c2
    assert c2 != c1


def test_attributes():
    c = Color((1, 0, 0), alpha=.6667)
    assert c.alpha == .6667
    assert c.red == 1
    assert c.green == 0
    assert c.blue == 0
    assert c.r == 255
    assert c.g == 0
    assert c.b == 0
    assert c.hue == 0
    assert c.saturation == 1
    assert c.lightness == .5
    assert 53.3 > c.cie_l > 53.2
    assert 80.2 > c.cie_a > 80.05
    assert 67.3 > c.cie_b > 67.2
    assert .5 > c.cie_x > .4
    assert .3 > c.cie_y > .2
    assert .1 > c.cie_z > 0
    assert .31 > c.y > .29
    assert -.16 > c.u > -.17
    assert c.v == .5
    assert c.name == 'red'
    assert c.luminance == 0.2126
    assert c.hex == "#f00"
    assert c.lhex == "#ff0000"
    assert c.hexa == "#f00a"
    assert c.lhexa == "#ff0000aa"
    assert c.cssrgb == "rgba(255, 0, 0, 0.6667)"
    assert c.set(alpha=1).cssrgb == "rgb(255, 0, 0)"
    assert c.csshsl == "hsla(0, 100%, 50%, 0.6667)"
    assert c.set(alpha=1).csshsl == "hsl(0, 100%, 50%)"
    assert c.csshwb == "hwb(0deg 0% 0% / 0.6667)"
    assert c.set(alpha=1).csshwb == "hwb(0deg 0% 0%)"
    assert c.csslab == "lab(53.24% 80.09 67.2 / 0.6667)"
    assert c.set(alpha=1).csslab == "lab(53.24% 80.09 67.2)"
    assert c.csslch == "lch(53.24% 104.5 39deg / 0.6667)"
    assert c.set(alpha=1).csslch == "lch(53.24% 104.5 39deg)"
    assert c.ansi == 196
    assert c.pltc == (1.0, 0.0, 0.0, 0.6667)
    assert c.termbg == "\x1b[48;2;255;0;0m"
    assert c.termfg == "\x1b[38;2;255;0;0m"
    assert c.hex == str(c)

    c = Color((1, 0, 0), alpha=.5)
    assert c.hexa == c.lhexa


def test_clipped():
    superwhite = Color(convert.LabTuple(250, 0, 0))
    assert superwhite == Color("white")
    assert superwhite.clipped


def test_attributes_frozen():
    c = Color("red")
    with pytest.raises(TypeError):
        c.rgb = (0, 1, 0)
    with pytest.raises(TypeError):
        c.hsl = (0, 1, 0)
    with pytest.raises(TypeError):
        c.hex = "#ff0000"
    with pytest.raises(TypeError):
        c.red = .2
    with pytest.raises(TypeError):
        c.alpha = .5


def test_invalid_attributes():
    class WrongColor(Color):
        cica = colors.ColorSpaceProperty("cica")
        cica_c = colors.ColorProperty("c", "cica")

    with pytest.raises(TypeError):
        wc = WrongColor()
        wc.cica

    with pytest.raises(TypeError):
        wc = WrongColor(cica=12)


def test_set():
    c = Color("red")
    c2 = c.set(green=1, blue=1)
    assert c2 == Color("white")

    c = Color("#a33")
    assert c.lighten().lightness > c.lightness
    assert c.darken().lightness < c.lightness
    assert c.saturate().saturation > c.saturation
    assert c.desaturate().saturation < c.saturation
    assert c.rotate().hue > c.hue


def test_distance():
    w = Color("white")
    b = Color("black")
    aw = Color("#feffff")

    assert w.distance(w) == 0
    assert w.distance(b) >= 100
    assert w.distance(aw) < 2

    assert w.similar(aw)
    assert not b.similar(aw)


def test_mix():
    r = Color("#f00")
    g = Color("#0f0")
    b = Color("#00f")

    rbrgb = r.mix(b)  # rgb default
    assert rbrgb.red < r.red
    assert rbrgb.red > b.red
    assert rbrgb.blue > r.blue
    assert rbrgb.blue < b.blue

    assert r.mix(b, cspace="hsl") == Color("#ff00ff")
    assert b.mix(r, cspace="hsl") == Color("#ff00ff")

    assert r.mix(b, .25) == Color("#bf0040")
    assert r.mix(b, .75) == Color("#4000bf")

    assert r.mix(g, gamma=2.2) == Color("#baba00")


def test_colorize():
    assert Color._colorize(Color("red")) == Color("red").rgb
    assert Color.colorize(Color("red")) == Color("red")
    assert Color.colorize(Color("red").rgb) == Color("red")
    assert Color.colorize(Color("red").hsl) == Color("red")
    assert Color.colorize(tuple(Color("red").rgb)) == Color("red")
    assert Color.colorize(tuple(Color("red").rgb256)) == Color("red")
    assert isinstance(Color.colorize({}), Color)


def test_gray():
    assert Color("black").gray() == Color("black")
    assert Color("white").gray() == Color("white")
    assert Color(convert.LabTuple(50, -10, 10)).gray() == Color(convert.LabTuple(50, 0, 0))


def test_contrast_ratio():
    assert about_the_same(Color("black").contrast_ratio(Color("white")), 21)
    assert about_the_same(Color("black").contrast_ratio(Color("black")), 1)


def test_adjust_contrast():
    for _ in range(10):
        r1, r2, g1, g2, b1, b2 = (random.random() for _ in range(6))
        c1 = Color(red=r1, green=g1, blue=b1)
        c2 = Color(red=r2, green=g2, blue=b2)

        ac1, ac2 = c1.adjust_contrast(c2)

        assert ac1.contrast_ratio(ac2) >= 4.5


def test_color_add():
    r = Color("#f00")
    g = Color("#0f0")

    assert r + g == Color("#ff0")
    assert r + g.rgb == Color("#ff0")
    assert r + g.hsl == Color("#fff")
    assert Color("#800000") + .5 == Color("#ff8080")


def test_color_radd():
    r = Color("#f00")
    g = Color("#0f0")

    assert g.rgb + r == Color("#ff0")
    assert .5 + Color("#800000") == Color("#ff8080")


def test_color_add_incompatible():
    with pytest.raises(TypeError):
        Color() + "color"


def test_color_mul():
    r = Color("#ff0100")
    g = Color("#01ff00")

    assert r * g == Color("#010100")
    assert r * g.rgb == Color("#010100")
    assert Color("#800000") * 2 == Color("#ff0000")


def test_color_rmul():
    r = Color("#ff0100")
    g = Color("#01ff00")

    assert g.rgb * r == Color("#010100")
    assert 2 * Color("#800000") == Color("#ff0000")


def test_color_mul_incompatible():
    with pytest.raises(TypeError):
        Color() * "color"


def test_color_sub():
    r = Color("#f00")
    g = Color("#0f0")

    assert Color("#ff0") - r == g
    assert Color("#ff0") - r.rgb == g
    assert Color("#ff0") - r.hsl == Color("black")
    assert r - .5 == Color("#800000")


def test_color_sub_incompatible():
    with pytest.raises(TypeError):
        Color() - "color"


def test_color_div():
    w = Color("#fff")
    g = Color("#0f0")

    assert g / w == g
    assert g / w.rgb == g
    assert g / 2 == Color("#008000")


def test_color_div_incompatible():
    with pytest.raises(TypeError):
        Color() / "color"


def test_color_complementary():
    r = Color("red")

    assert r.complementary() == Color("#0ff")
    assert r.complementary("lab") == Color("#0090e0")
    assert r.complementary("lch") == Color("#2e8000")
    assert r.complementary("xyz") == Color("#34fff7")


def test_displayimage():
    img = Color("green").displayimage

    assert len(img)
    assert len(img[0])


def test_termimage():
    img = Color("green").termimage

    assert isinstance(img, str)


def test_info():
    info = Color("green").info

    assert "green" in info
    assert "#008000" in info


def test_display():
    dpinfo = Color("green").display

    assert "green" in dpinfo
    assert "#008000" in dpinfo


def test_print():
    stream = io.StringIO()
    Color("red").print(stream=stream)

    assert "#ff0000" in stream.getvalue()

    stream = io.StringIO()
    Color("red").print(force_ansi=True, stream=stream)

    assert "#ff0000" in stream.getvalue()
    assert "red" in stream.getvalue()
