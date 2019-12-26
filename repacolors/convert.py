import colorsys
import math

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


def rgbdistance(c1, c2):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)


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


rgb2ycbcr = rgb2yuv
ycbcr2rgb = yuv2rgb
rgb2yiq = colorsys.rgb_to_yiq
yiq2rgb = colorsys.yiq_to_rgb
rgb2hsv = colorsys.rgb_to_hsv
hsv2rgb = colorsys.hsv_to_rgb
