"""Conversion between different color spaces

http://easyrgb.com/en/math.php
"""

import colorsys

FLOAT_ERROR = 0.00005

ANSI16 = [
    (0, 0, 0),
    (.5, 0, 0),
    (0, .5, 0),
    (.5, .5, 0),
    (0, 0, .5),
    (.5, 0, .5),
    (0, .5, .5),
    (.75, .75, .75),
    (.5, .5, .5),
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


def distance(c1, c2):
    """Color distance
    Can be used with RGB or CIE-Lab values (CIE76 later case)
    https://en.wikipedia.org/wiki/Color_difference#CIELAB_%CE%94E*

    For Lab colors: diff ~ 2.3 - just noticeable difference
    """

    return ((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2) ** .5


def ansi2rgb(ansicolor):
    if ansicolor < 16:
        # first 16 colors - special case
        return ANSI16[ansicolor]
    elif ansicolor < 232:
        # colors
        i = ansicolor - 16
        ar = i // 36
        ag = (i - ar * 36) // 6
        ab = (i - ar * 36 - ag * 6)
        return tuple((55 + 40 * x) / 255 if x > 0 else 0 for x in (ar, ag, ab))
    elif ansicolor < 256:
        # grayscale
        i = ansicolor - 231
        c = ((256 / 32 * i) + (i - 1) * 2) / 255
        return c, c, c

    # out of range
    return 0, 0, 0


def rgb2ansi(r, g, b):
    coli = tuple(int(255 * x) for x in (r, g, b))
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
                res.append(closest)
                break

    ansicol = 16 + sum(x[1] * 6**(2 - x[0]) for x in enumerate(res))

    # check grayscale
    if abs(coli[0] - coli[1]) < 10 and \
       abs(coli[1] - coli[2]) < 10 and \
       abs(coli[0] - coli[2]) < 10:
        avg = sum(coli) / 3
        for i in range(24):
            c = (256 / 32 * (i + 1)) + i * 2
            if abs(c - avg) <= 5:
                ansigray = 232 + i
                if rgbdistance(coli, res) > rgbdistance(coli, (c, c, c)):
                    ansicol = ansigray

    return ansicol


def rgb2hex(r, g, b, force_long=False):
    hx = ''.join(["%02x" % int(c * 255 + 0.5)
                  for c in (r, g, b)])

    if not force_long and hx[0::2] == hx[1::2]:
        hx = ''.join(hx[0::2])

    return "#%s" % hx


def hex2rgb(hexcolor):
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

    return tuple([float(int(v, 16)) / 255 for v in (r, g, b)])


def rgb2yuv(r, g, b):  # 0..1 range
    y = .299 * r + .587 * g + .114 * b
    u = .5 - .168736 * r - .331364 * g + .5 * b
    v = .5 + .5 * r - .418688 * g - .081312 * b
    return y, u, v


def yuv2rgb(y, u, v):
    r = y + 1.402 * (v - .5)
    g = y - .34414 * (u - .5) - .71414 * (v - .5)
    b = y + 1.772 * (u - .5)
    return r, g, b


def rgb2hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def hsl2rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r, g, b


def rgb2xyz(r, g, b):
    vr, vg, vb = tuple(((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92 for c in (r, g, b))

    x = 100 * (0.4124 * vr + 0.3576 * vg + 0.1805 * vb)
    y = 100 * (0.2126 * vr + 0.7152 * vg + 0.0722 * vb)
    z = 100 * (0.0193 * vr + 0.1192 * vg + 0.9505 * vb)

    return x, y, z


def xyz2rgb(x, y, z):
    x, y, z = x / 100, y / 100, z / 100

    vr = x * 3.2406 + y * -1.5372 + z * -0.4986
    vg = x * -0.9689 + y * 1.8758 + z * 0.0415
    vb = x * 0.0557 + y * -0.2040 + z * 1.0570

    r, g, b = tuple(
        1.055 * c ** (1 / 2.4) - 0.055 
        if c > 0.0031308 
        else 12.92 * c 
        for c in (vr, vg, vb)
    )

    return r, g, b


def xyz2lab(x, y, z, whitepoint=D65):
    x = x / whitepoint[0]
    y = y / whitepoint[1]
    z = z / whitepoint[2]

    vx, vy, vz = tuple(
        c ** (1 / 3)
        if c > 0.008856
        else 7.787 * c + 16 / 116
        for c in (x, y, z)
    )

    return 116 * vy - 16, 500 * (vx - vy), 200 * (vy - vz)


def lab2xyz(l, a, b, whitepoint=D65):
    vy = (l + 16) / 116
    vx = a / 500 + vy
    vz = vy - b / 200

    x, y, z = tuple(
        c ** 3
        if c > 0.206893
        else (c - 16 / 116) / 7.787
        for c in (vx, vy, vz)
    )

    return x * whitepoint[0], y * whitepoint[1], z * whitepoint[2]


def rgb2lab(r, g, b, whitepoint=D65):
    return xyz2lab(*rgb2xyz(r, g, b), whitepoint)


def lab2rgb(l, a, b, whitepoint=D65):
    return xyz2rgb(*lab2xyz(l, a, b, whitepoint))


def rgb2cmyk(r, g, b):
    vc, vm, vy = tuple(1 - v for v in (r, g, b))
    k = 1
    for v in (vc, vm, vy):
        if v < k:
            k = v

    if k == 1:
        c, m, y = 0, 0, 0
    else:
        c, m, y = tuple((v - k) / (1 - k) for v in (vc, vm, vy))

    return c, m, y, k


def cmyk2rgb(c, m, y, k):
    r, g, b = tuple(1 - (v * (1 - k) + k) for v in (c, m, y))

    return r, g, b


rgb2ycbcr = rgb2yuv
ycbcr2rgb = yuv2rgb
rgb2yiq = colorsys.rgb_to_yiq
yiq2rgb = colorsys.yiq_to_rgb
rgb2hsv = colorsys.rgb_to_hsv
hsv2rgb = colorsys.hsv_to_rgb
