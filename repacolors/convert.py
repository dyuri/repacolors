"""Conversion between different color spaces

http://easyrgb.com/en/math.php
"""

import colorsys
from typing import Tuple, NamedTuple

ANSI16 = [
    (0, 0, 0),
    (0.5, 0, 0),
    (0, 0.5, 0),
    (0.5, 0.5, 0),
    (0, 0, 0.5),
    (0.5, 0, 0.5),
    (0, 0.5, 0.5),
    (0.75, 0.75, 0.75),
    (0.5, 0.5, 0.5),
    (1, 0, 0),
    (0, 1, 0),
    (1, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (0, 1, 1),
    (1, 1, 1),
]

# whitepoints
D50 = (96.422, 100.000, 82.521)
D55 = (95.682, 100.000, 92.149)
D65 = (95.047, 100.000, 108.883)
D75 = (94.972, 100.000, 122.638)

CTuple = Tuple[float, ...]


class HSLTuple(NamedTuple):
    hue: float
    saturation: float
    lightness: float


class RGBTuple(NamedTuple):
    red: float
    green: float
    blue: float


class YUVTuple(NamedTuple):
    y: float
    u: float
    v: float


class XYZTuple(NamedTuple):
    x: float
    y: float
    z: float


class LabTuple(NamedTuple):
    l: float
    a: float
    b: float


class CMYKTuple(NamedTuple):
    c: float
    m: float
    y: float
    k: float


def distance(c1: CTuple, c2: CTuple) -> float:
    """Color distance
    Can be used with RGB or CIE-Lab values (CIE76 later case)
    https://en.wikipedia.org/wiki/Color_difference#CIELAB_%CE%94E*

    For Lab colors: diff ~ 2.3 - just noticeable difference
    """

    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def ansi2rgb(ansicolor: int) -> RGBTuple:
    if 0 <= ansicolor < 16:
        # first 16 colors - special case
        return RGBTuple(*ANSI16[ansicolor])
    elif 16 <= ansicolor < 232:
        # colors
        i = ansicolor - 16
        ar = i // 36
        ag = (i - ar * 36) // 6
        ab = i - ar * 36 - ag * 6
        return RGBTuple(*((55 + 40 * x) / 255 if x > 0 else 0 for x in (ar, ag, ab)))
    elif 232 <= ansicolor < 256:
        # grayscale
        i = ansicolor - 231
        c = ((256 / 32 * i) + (i - 1) * 2) / 255
        return RGBTuple(c, c, c)

    # out of range
    return RGBTuple(0, 0, 0)


def rgb2ansi(color: CTuple) -> int:
    r, g, b = color
    coli = tuple(float(int(255 * x)) for x in (r, g, b))
    steps = [0] + [95 + 40 * x for x in range(5)]

    res = []
    for c in coli:
        for i in range(len(steps)):
            p, n = steps[i], steps[i + 1]
            if p <= c <= n:
                dp, dn = abs(p - c), abs(n - c)
                if dp < dn:
                    closest = i
                else:
                    closest = i + 1
                res.append(float(closest))
                break

    ansicol = 16 + sum(x[1] * 6 ** (2 - x[0]) for x in enumerate(res))

    # check grayscale
    if (
        abs(coli[0] - coli[1]) < 10
        and abs(coli[1] - coli[2]) < 10
        and abs(coli[0] - coli[2]) < 10
    ):
        avg = sum(coli) / 3
        for i in range(24):
            cc = (256 / 32 * (i + 1)) + i * 2
            if abs(cc - avg) <= 5:
                ansigray = 232 + i
                c1 = ansi2rgb(ansicol)
                c2 = ansi2rgb(ansigray)
                if distance(color, c1) > distance(color, c2):
                    ansicol = ansigray

    return int(ansicol)


def rgb2hex(color: CTuple, force_long: bool = False) -> str:
    r, g, b = color
    hx = "".join(["%02x" % int((c + .0025) * 255) for c in (r, g, b)])

    if not force_long and hx[0::2] == hx[1::2]:
        hx = "".join(hx[0::2])

    return "#%s" % hx


def hex2rgb(hexcolor: str) -> RGBTuple:
    try:
        rgb = hexcolor[1:]

        if len(rgb) == 6:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
        elif len(rgb) == 3:
            r, g, b = rgb[0] * 2, rgb[1] * 2, rgb[2] * 2
        else:
            raise ValueError()
    except Exception:
        raise ValueError("Invalid value %r provided for rgb color." % hexcolor)

    return RGBTuple(*(float(int(v, 16)) / 255 for v in (r, g, b)))


def rgb2yuv(color: RGBTuple) -> YUVTuple:
    r, g, b = color
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = - 0.168736 * r - 0.331364 * g + 0.5 * b
    v = 0.5 * r - 0.418688 * g - 0.081312 * b
    return YUVTuple(y, u, v)


def yuv2rgb(color: YUVTuple) -> RGBTuple:
    y, u, v = color
    r = y + 1.402 * v
    g = y - 0.34414 * u - 0.71414 * v
    b = y + 1.772 * u
    return RGBTuple(r, g, b)


def rgb2hsl(color: RGBTuple) -> HSLTuple:
    h, l, s = colorsys.rgb_to_hls(*color)
    return HSLTuple(h, s, l)


def hsl2rgb(color: HSLTuple) -> RGBTuple:
    h, s, l = color
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return RGBTuple(r, g, b)


def rgb2xyz(color: RGBTuple) -> XYZTuple:
    vr, vg, vb = tuple(
        ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in color
    )

    x = 0.4124 * vr + 0.3576 * vg + 0.1805 * vb
    y = 0.2126 * vr + 0.7152 * vg + 0.0722 * vb
    z = 0.0193 * vr + 0.1192 * vg + 0.9505 * vb

    return XYZTuple(x, y, z)


def xyz2rgb(color: XYZTuple) -> RGBTuple:
    x, y, z = color

    vr = x * 3.2406 + y * -1.5372 + z * -0.4986
    vg = x * -0.9689 + y * 1.8758 + z * 0.0415
    vb = x * 0.0557 + y * -0.2040 + z * 1.0570

    r, g, b = tuple(
        1.055 * c ** (1 / 2.4) - 0.055 if c > 0.0031308 else 12.92 * c
        for c in (vr, vg, vb)
    )

    return RGBTuple(r, g, b)


def xyz2lab(color: XYZTuple, whitepoint: CTuple = D65) -> LabTuple:
    x, y, z = tuple(100 * c[0] / c[1] for c in zip(color, whitepoint))

    vx, vy, vz = tuple(
        c ** (1 / 3) if c > 0.008856 else 7.787 * c + 16 / 116 for c in (x, y, z)
    )

    return LabTuple(116 * vy - 16, 500 * (vx - vy), 200 * (vy - vz))


def lab2xyz(color: LabTuple, whitepoint: CTuple = D65) -> XYZTuple:
    l, a, b = color
    vy = (l + 16) / 116
    vx = a / 500 + vy
    vz = vy - b / 200

    x, y, z = tuple(
        c ** 3 if c > 0.206893 else (c - 16 / 116) / 7.787 for c in (vx, vy, vz)
    )

    return XYZTuple(x * whitepoint[0] / 100, y * whitepoint[1] / 100, z * whitepoint[2] / 100)


def rgb2lab(color: RGBTuple, whitepoint: CTuple = D65) -> LabTuple:
    return xyz2lab(rgb2xyz(color), whitepoint)


def lab2rgb(color: LabTuple, whitepoint: CTuple = D65) -> RGBTuple:
    return xyz2rgb(lab2xyz(color, whitepoint))


def rgb2cmyk(color: RGBTuple) -> CMYKTuple:
    vc, vm, vy = tuple(1 - v for v in color)
    k = 1.0
    for v in (vc, vm, vy):
        if v < k:
            k = v

    if k == 1.0:
        print("cica")
        c, m, y = 0.0, 0.0, 0.0
    else:
        c, m, y = tuple((v - k) / (1 - k) for v in (vc, vm, vy))

    return CMYKTuple(c, m, y, k)


def cmyk2rgb(color: CMYKTuple) -> RGBTuple:
    c, m, y, k = color
    return RGBTuple(*(1 - (v * (1 - k) + k) for v in (c, m, y)))


# add these as well since we have them for "free"
def rgb2yiq(color: RGBTuple) -> CTuple:
    return colorsys.rgb_to_yiq(*color)


def yiq2rgb(color: CTuple) -> RGBTuple:
    return RGBTuple(*colorsys.yiq_to_rgb(*color))


def rgb2hsv(color: RGBTuple) -> CTuple:
    return colorsys.rgb_to_hsv(*color)


def hsv2rgb(color: CTuple) -> RGBTuple:
    return RGBTuple(*colorsys.hsv_to_rgb(*color))
