from . import colors
from . import convert
from collections import namedtuple


HSLColor = namedtuple('HSLColor', ('hue', 'saturation', 'lightness'))
RGBColor = namedtuple('RGBColor', ('red', 'green', 'blue'))


def equal_hex(c1, c2):
    return c1.lhex == c2.lhex


def equal_hsl(c1, c2):
    return c1.csshsl == c2.csshsl


def equal_hsla(c1, c2):
    return c1.csshsla == c2.csshsla


def cmul(t, n):
    if not isinstance(t, tuple):
        raise TypeError('Tuple/namedtuple required.')

    cls = t.__class__

    return cls(*tuple(v * n for v in t))


# TODO not the best name, gradient is different
def gradient(frm, to, steps=10, prop='hsl'):
    if steps < 1:
        raise ValueError(f"Gradient steps should be more than 1 ({steps})")

    p1, p2 = getattr(frm, prop), getattr(to, prop)
    cls = p1.__class__
    deltac = cls(*tuple((p[1] - p[0]) / steps for p in zip(p1, p2)))

    return (frm + cmul(deltac, i) for i in range(steps + 1))


class ColorProperty():

    def __init__(self, name='hue', mainprop='_hsl'):
        self.name = name
        self.mainprop = mainprop

    def __get__(self, obj, objtype):
        prop = getattr(obj, self.mainprop)
        return getattr(prop, self.name)

    def __set__(self, obj, val):
        prop = getattr(obj, self.mainprop)
        proplist = list(prop)
        proptype = prop.__class__
        idx = prop._fields.index(self.name)
        proplist[idx] = val
        setattr(obj, self.mainprop, proptype(*proplist))


# TODO - make it immutable - modifications should return a new color
class Color():
    """Color object

    Can be initialized with many kind of color definitions, and output different
    formats as well.

    Internal representation is HSL.
    """

    red = ColorProperty('red', 'rgb')
    green = ColorProperty('green', 'rgb')
    blue = ColorProperty('blue', 'rgb')
    hue = ColorProperty('hue', 'hsl')
    saturation = ColorProperty('saturation', 'hsl')
    lightness = ColorProperty('lightness', 'hsl')

    def __init__(self, colordef=None, equality=equal_hex, **kwargs):
        self._hsl = HSLColor(0, 0, 0)
        self._rgb = RGBColor(0, 0, 0)
        self._alpha = 1  # TODO alpha support

        self._eq = equality

        # from color
        if isinstance(colordef, Color):
            self.hue = colordef.hue

        # from RGBColor
        elif isinstance(colordef, RGBColor):
            self.rgb = colordef

        # from HSLColor
        elif isinstance(colordef, HSLColor):
            self.hue = colordef

        # from rgb tuple
        elif isinstance(colordef, tuple):
            if colordef[0] > 1 or \
               colordef[1] > 1 or \
               colordef[2] > 1:
                self.rgb = tuple(c / 255 for c in colordef)
            else:
                self.rgb = colordef

        # from bytes
        elif isinstance(colordef, bytes):
            if len(colordef) == 3:
                self.rgb = tuple(c / 255 for c in colordef)

        # from ansi color index
        elif isinstance(colordef, int):
            self.rgb = convert.ansi2rgb(colordef)

        elif isinstance(colordef, str):
            # from hex color
            if colordef.startswith('#'):
                self.rgb = convert.hex2rgb(colordef)
            elif colordef.startswith('rgb'):
                pass  # TODO rgb + rgba CSS
            elif colordef.startswith('hsl'):
                pass  # TODO hsl + hsla CSS
            else:
                pass  # TODO named colors

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def colorize(cls, obj):
        pass  # TODO pick "unique" color for hashable object

    def gradient(self, to, steps=10, prop='hsl'):
        return gradient(self, to, steps, prop)

    def closest_named(self, num=3):
        pass  # TODO return closest named colors

    def distance(self, other):
        return convert.distance(self.lab, other.lab)

    def similar(self, other):
        return self.distance(other) < 2.3

    @property
    def name(self):
        # TODO return color name for exact match
        return self.hex

    @property
    def rgb(self):
        return self._rgb

    @rgb.setter
    def rgb(self, rgb):
        self._rgb = RGBColor(*rgb)
        hue = self.hue
        self._hsl = HSLColor(*convert.rgb2hsl(*rgb))
        if self._hsl.saturation == 0:
            self._hsl = HSLColor(hue, self._hsl.saturation, self._hsl.lightness)

    @property
    def rgb256(self):
        return RGBColor(*tuple(round(255 * c + 0.0001) for c in self._rgb))

    @property
    def hsl(self):
        return self._hsl

    @hsl.setter
    def hsl(self, hsl):
        self._hsl = HSLColor(*hsl)
        self._rgb = RGBColor(*convert.hsl2rgb(*hsl))

    @property
    def luminance(self):
        rgb = self.rgb
        rgb_lum = tuple(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb)
        return 0.2126 * rgb_lum[0] + 0.7152 * rgb_lum[1] + 0.0722 * rgb_lum[2]

    def contrast_ratio(self, other):
        """WCAG relative contrast ratio

        contrast_ratio > 4.5:1 - AA
        contrast_ratio > 7:1 - AAA
        """
        l1, l2 = self.luminance, other.luminance
        if l2 > l1:
            l1, l2 = l2, l1

        return (l1 + 0.05) / (l2 + 0.05)

    @property
    def lhex(self):
        return convert.rgb2hex(*self.rgb, True)

    @property
    def hex(self):
        return convert.rgb2hex(*self.rgb, False)

    @property
    def ansi(self):
        return convert.rgb2ansi(*self.rgb)

    @property
    def hsv(self):
        return convert.rgb2hsv(*self.rgb)

    @property
    def yuv(self):
        return convert.rgb2yuv(*self.rgb)

    @property
    def yiq(self):
        return convert.rgb2yiq(*self.rgb)

    @property
    def lab(self):
        return convert.rgb2lab(*self.rgb)

    @property
    def xyz(self):
        return convert.rgb2xyz(*self.rgb)

    @property
    def cmyk(self):
        return convert.rgb2cmyk(*self.rgb)

    @property
    def cssrgb(self):
        rgb256 = self.rgb256
        return f'rgb({rgb256.red}, {rgb256.green}, {rgb256.blue})'

    @property
    def cssrgba(self):
        rgb256 = self.rgb256
        return f'rgb({rgb256.red}, {rgb256.green}, {rgb256.blue}, {self.alpha:.5g})'

    @property
    def csshsl(self):
        return f'hsl({int(360 * self.hue)}, {(100 * self.saturation):.4g}%, {(100 * self.lightness):.4g}%)'

    @property
    def csshsla(self):
        return f'hsla({int(360 * self.hue)}, {(100 * self.saturation):.4g}%, {(100 * self.lightness):.4g}%, {self.alpha:.5g})'

    @property
    def alpha(self):
        return self._alpha

    def __str__(self):
        return self.hex

    def __repr__(self):
        return f'<Color {self.csshsla}>'

    def __eq__(self, other):
        if isinstance(other, Color):
            return self._eq(self, other)
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Color):
            hsl = tuple(p[0] + p[1] for p in zip(self.hsl, other.hsl))
            return Color(hsl=(1 if hsl[0] == 1 else hsl[0] % 1, min(hsl[1], 1), min(hsl[2], 1)))
        elif isinstance(other, HSLColor):
            hsl = tuple(p[0] + p[1] for p in zip(self.hsl, other))
            return Color(hsl=(1 if hsl[0] == 1 else hsl[0] % 1, min(hsl[1], 1), min(hsl[2], 1)))
        elif isinstance(other, RGBColor):
            rgb = tuple(min(p[0] + p[1], 1) for p in zip(self.rgb, other))
            return Color(rgb=rgb)

        raise TypeError(f"Cannot add '{type(other)}' to 'Color'")

    def __sub__(self, other):
        # TODO see __add__
        if not isinstance(other, Color):
            raise TypeError(f"Cannot substract '{type(other)}' from 'Color'")

        hsl = tuple(p[0] - p[1] for p in zip(self.hsl, other.hsl))
        return Color(hsl=(1 if hsl[0] == 1 else hsl[0] % 1, max(hsl[1], 0), max(hsl[2], 0)))

    def __mul__(self, n):
        if not isinstance(n, int) or isinstance(n, float):
            raise TypeError(f"Cannot multiply 'Color' with '{type(n)}'")
        if n < 0:
            raise TypeError("Cannot multiply 'Color' with negative values")

        hsl = tuple(p * n for p in self.hsl)
        return Color(hsl=(1 if hsl[0] == 1 else hsl[0] % 1, min(hsl[1], 1), min(hsl[2], 1)))

    def __rmul__(self, n):
        return self * n

    def _ansibg(self):
        rgb = self.rgb256
        return f"\x1b[48;2;{rgb.red};{rgb.green};{rgb.blue}m   \x1b[0m"
