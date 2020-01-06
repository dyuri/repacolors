from repacolors import Color, convert


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

    rgbt = (1, 0, 0, 0)
    c = Color(rgbt)
    assert rgbt[:3] == c.rgb
    assert c.lhex == "#ff0000"
    assert c.alpha == 0

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

    # TODO rgb + hsl css definitions

    c = Color("red")
    assert c.lhex == "#ff0000"

    # whatever, from hash
    c = Color("whatever")
    assert isinstance(c, Color)


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
    c1 = Color("red", equality=Color.equal_hex)
    c2 = Color("#ff0000", equality=Color.equal_hex)
    assert c1 == c2

    c1 = Color("red", equality=Color.equal_hsl)
    c2 = Color("#ff0000", equality=Color.equal_hsl)
    assert c1 == c2

    c1 = Color("red", equality=Color.equal_hsla)
    c2 = Color("#ff0000", equality=Color.equal_hsla)
    assert c1 == c2

    c1 = Color("red", equality=Color.equal_hash)
    c2 = Color("#ff0000", equality=Color.equal_hash)
    assert c1 == c2


def test_equality_negative():
    c1 = Color("#ff0000")
    c2 = Color("#ff0001")
    assert c1 != c2

    c1 = Color("black", equality=Color.equal_hsl, hue=.6666)
    c2 = Color("black", equality=Color.equal_hex, hue=0)
    assert c2 == c1
    assert c1 != c2

    c1 = Color("red", equality=Color.equal_hsl, alpha=.5)
    c2 = Color("red", equality=Color.equal_hsla, alpha=1)
    assert c1 == c2
    assert c2 != c1

    c1 = Color("cyan", equality=Color.equal_hsl, hue=.501)
    c2 = Color("cyan", equality=Color.equal_hash)
    print(repr(c1), repr(c2))
    print(hash(c1), hash(c2))
    assert c1 == c2
    assert c2 != c1


def test_pick():
    c = Color.pick(picker=["/usr/bin/echo", "#ff0000"])
    assert c.lhex == "#ff0000"
