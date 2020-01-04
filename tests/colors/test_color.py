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

    # TODO ... xyz, yuv, hex, ansi, ...
