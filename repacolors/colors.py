import json
import os
import sys
import math
import re
import subprocess  # nosec
from itertools import zip_longest
from typing import Dict, Any, Optional, Callable, Iterator, List, Union, Tuple
from . import convert
from . import terminal
from . import distance
from . import blend
from . import ops
from .types import *

DIR = os.path.dirname(os.path.realpath(__file__))
CSSJSON = os.path.join(DIR, "css-color-names.json")

with open(CSSJSON, "r") as f:
    CSSNAME2HEX = json.load(f)

HEX2CSSNAME = dict((hx, name) for name, hx in CSSNAME2HEX.items())


def name2hex(name: str) -> str:
    return CSSNAME2HEX.get(name, None)


def hex2name(hx: str) -> str:
    return HEX2CSSNAME.get(hx, None)


# TODO
COLORCACHE: Dict[str, Dict[str, Any]] = {}


# TODO
def get_color(hx, cspace="rgb", container=COLORCACHE):
    if hx in container:
        color = container[hx]
    else:
        color = {"hex": hx, "rgb": convert.hex2rgb(hx), "name": hex2name(hx)}
        container[hx] = color

    if cspace not in color and hasattr(convert, f"rgb2{cspace}"):
        color[cspace] = getattr(convert, f"rgb2{cspace}")(RGBTuple(*color["rgb"]))

    return color


# TODO
def closest(col: CTuple, n: int = 3, cspace: str = "rgb"):
    named_colors = HEX2CSSNAME.keys()
    chx = convert.rgb2hex(RGBTuple(*col), True)
    if cspace != "rgb":
        col = getattr(convert, f"rgb2{cspace}")(*col)
    closests = []

    for nch in named_colors:
        if chx == nch:
            continue
        nc = get_color(nch, cspace)
        distance = distance.distance(col, nc[cspace])
        closests.append({"color": nc, "distance": distance})
        # not the most efficient way, but...
        closests.sort(key=lambda c: c["distance"])
        closests = closests[:n]

    return closests


class ColorProperty:
    def __init__(self, name, mainprop):
        self.name = name
        self.mainprop = mainprop

    def __get__(self, obj: "Color", objtype: type):
        prop = getattr(obj, self.mainprop)
        return getattr(prop, self.name)

    def __set__(self, obj: "Color", val: Any):
        if not obj._initialized:
            prop = getattr(obj, self.mainprop)
            proplist = list(prop)
            proptype = prop.__class__
            idx = prop._fields.index(self.name)
            proplist[idx] = val
            setattr(obj, self.mainprop, proptype(*proplist))
        else:
            raise TypeError("Should not modify an existing 'Color' instance")


class ColorSpaceProperty:
    def __init__(self, name: str = "lab"):
        self.name = name
        self.privname = "_" + self.name

    def __get__(self, obj: "Color", objtype: type):
        privattr = getattr(obj, self.privname, None)

        # already cached
        if privattr is not None:
            return privattr

        # not cached yet, check for convert function
        convertfn = getattr(convert, f"rgb2{self.name}", None)
        if convertfn:
            privattr = convertfn(obj._rgb)
            setattr(obj, self.privname, privattr)
            return privattr

        # cannot convert
        raise TypeError(f"Cannot convert 'Color' to {self.name} format")

    def __set__(self, obj: "Color", val: Any):
        if not obj._initialized:
            # check for convert function
            convertfn = getattr(convert, f"{self.name}2rgb", None)
            if convertfn:
                rgb = convertfn(val)
                obj.rgb = rgb
                setattr(obj, self.privname, val)
            else:
                # no conversion function found
                raise TypeError(f"Cannot convert {self.name} format to 'Color'")
        else:
            raise TypeError("Should not modify an existing 'Color' instance")


class Color(terminal.TerminalColor):
    """Color object

    Can be initialized with many kind of color definitions, and output different
    formats as well.
    """

    DISPLAY_HEIGHT = 12
    DISPLAY_WIDTH = 12
    DISPLAY_BORDER = 2

    red = ColorProperty("red", "rgb")
    green = ColorProperty("green", "rgb")
    blue = ColorProperty("blue", "rgb")
    r = ColorProperty("red", "rgb256")
    g = ColorProperty("green", "rgb256")
    b = ColorProperty("blue", "rgb256")
    hue = ColorProperty("hue", "hsl")
    saturation = ColorProperty("saturation", "hsl")
    lightness = ColorProperty("lightness", "hsl")
    whiteness = ColorProperty("whiteness", "hwb")
    blackness = ColorProperty("blackness", "hwb")
    value = ColorProperty("value", "hsv")
    cie_l = ColorProperty("l", "lab")
    cie_a = ColorProperty("a", "lab")
    cie_b = ColorProperty("b", "lab")
    cie_c = ColorProperty("c", "lch")
    cie_h = ColorProperty("h", "lch")
    cie_x = ColorProperty("x", "xyz")
    cie_y = ColorProperty("y", "xyz")
    cie_z = ColorProperty("z", "xyz")
    y = ColorProperty("y", "yuv")
    u = ColorProperty("u", "yuv")
    v = ColorProperty("v", "yuv")

    hex = ColorSpaceProperty("hex")
    hsv = ColorSpaceProperty("hsv")
    hwb = ColorSpaceProperty("hwb")
    ansi = ColorSpaceProperty("ansi")
    xyz = ColorSpaceProperty("xyz")
    lab = ColorSpaceProperty("lab")
    lch = ColorSpaceProperty("lch")
    yuv = ColorSpaceProperty("yuv")
    hsv = ColorSpaceProperty("hsv")
    yiq = ColorSpaceProperty("yiq")
    cmyk = ColorSpaceProperty("cmyk")

    def __init__(
        self,
        colordef: Any = None,
        alpha: float = None,
        equality: Optional[Callable[["Color", "Color"], bool]] = None,
        **kwargs,
    ):
        self._hsl = HSLTuple(0, 0, 0)
        self._rgb = RGBTuple(0, 0, 0)
        self._alpha = 1.0
        self.cspace = "hsl"

        self._initialized = False

        self._eq = equality if equality is not None else ops.equal_hex

        # from color
        if isinstance(colordef, Color):
            self._hsl = colordef._hsl
            self.rgb = colordef._rgb
            self.alpha = colordef.alpha
            self.cspace = colordef.cspace

        # from tuple
        elif isinstance(colordef, (tuple, list)):
            self._init_tuple(colordef)

        # from bytes
        elif isinstance(colordef, bytes):
            self._init_bytes(colordef)

        # from str
        elif isinstance(colordef, str):
            self._init_str(colordef)

        # override alpha
        if alpha is not None:
            self._alpha = alpha

        # additional parameters
        for k, v in kwargs.items():
            setattr(self, k, v)

        self._initialized = True

    def _init_tuple(self, colordef: Union[tuple, list]):
        for cspace, ctype in COLORSPACES.items():
            if isinstance(colordef, ctype):
                setattr(self, cspace, colordef)
                self.cspace = cspace
                break
        else:
            if len(colordef) >= 3:
                if abs(colordef[0]) > 1 or abs(colordef[1]) > 1 or abs(colordef[2]) > 1:
                    self.rgb256 = tuple(v % 256 for v in colordef[:3])
                else:
                    self.rgb = tuple(abs(v) for v in colordef[:3])
                self.cspace = "rgb"

                if len(colordef) >= 4:
                    self.alpha = colordef[3]

    def _init_bytes(self, colordef: bytes):
        if len(colordef) == 3:
            self.rgb256 = RGBTuple(*tuple(colordef))
            self.cspace = "rgb"
        elif len(colordef) == 4:
            self.rgb256 = RGBTuple(*tuple(colordef[:3]))
            self.alpha = list(colordef)[3] / 255
            self.cspace = "rgb"

    def _init_str(self, colordef: str):
        # from hex color
        if colordef.startswith("#"):
            self.hex = colordef
            self.cspace = "rgb"
            if len(colordef) == 5:
                self.alpha = int(colordef[4] * 2, 16) / 255
            elif len(colordef) == 9:
                self.alpha = int(colordef[7:9], 16) / 255
        elif (
            colordef.startswith("rgb")
            or colordef.startswith("hsl")
            or colordef.startswith("hwb")
            or colordef.startswith("lab")
        ):
            mode = colordef[:3]
            clr, self.alpha = self.parse_css_color_values(colordef, mode)
            setattr(self, mode, clr)
            self.cspace = mode
        elif colordef.startswith("gray"):
            begin = colordef.index("(")
            end = colordef.index(")")
            cnt = colordef[begin + 1 : end]

            cnt = re.sub(r"\s+", " ", cnt.replace("/", " ")).strip()
            values = [float(v.strip()) for v in cnt.split(" ")]

            self.lab = LabTuple(values[0], 0, 0)
            self.alpha = values[1] if len(values) > 1 else 1.0
        else:
            hx = name2hex(colordef)
            if hx:
                self.rgb = convert.hex2rgb(hx)
                self.cspace = "rgb"
                self._name = colordef
            else:
                self.rgb = Color._colorize(colordef)
                self.cspace = "rgb"

    @staticmethod
    def parse_css_color_values(
        csscolordef: str, mode: str = "rgb"
    ) -> Tuple[CTuple, float]:
        """Parse CSS color definition

        https://developer.mozilla.org/en-US/docs/Web/CSS/color_value
        """
        begin = csscolordef.index("(")
        end = csscolordef.index(")")
        cnt = csscolordef[begin + 1 : end]
        alpha = 1.0

        if "," in cnt:
            cnt = re.sub(r"\s+", " ", cnt).strip()
            values = [v.strip() for v in cnt.split(",")]
        else:
            cnt = cnt.replace("/", " ").strip()
            cnt = re.sub(r"\s+", " ", cnt)
            values = [v.strip() for v in cnt.split(" ")]

        if len(values) > 3:
            alpha = Color.parse_css_color_value(values[3], "alpha")

        cls = COLORSPACES.get(mode.lower(), RGBTuple)
        color = cls(*tuple(Color.parse_css_color_value(v, mode) for v in values[:3]))

        return color, alpha

    @staticmethod
    def parse_css_color_value(csscolorvalue: str, mode: str = "rgb") -> float:
        if csscolorvalue[-1] == "%":
            if mode.lower() == "lab":
                return float(csscolorvalue[:-1])
            return float(csscolorvalue[:-1]) / 100
        elif mode.lower() == "alpha":
            return float(csscolorvalue)
        elif mode.lower() in ["hsl", "hwb"]:
            # hue only
            if csscolorvalue[-4:] == "turn":
                return float(csscolorvalue[:-4])
            elif csscolorvalue[-3:] == "rad":
                return float(csscolorvalue[:-3]) / (2 * math.pi)
            elif csscolorvalue[-3:] == "deg":
                csscolorvalue = csscolorvalue[:-3]

            # degree
            return float(csscolorvalue) / 360
        elif mode.lower() == "lab":
            return float(csscolorvalue)

        # rgb
        return float(csscolorvalue) / 255

    @classmethod
    def pick(cls, picker: Union[str, List[str]] = "xcolor") -> "Color":
        # TODO optionally integrate chameleon (https://github.com/seebye/chameleon)
        # TODO copy to clipboard
        # TODO draw color wheel
        # TODO => separate module
        proc = subprocess.Popen(picker, stdout=subprocess.PIPE)  # nosec
        res = proc.communicate()[0].strip().decode()
        return cls(res)

    @classmethod
    def _colorize(cls, obj: Any) -> RGBTuple:
        if isinstance(obj, RGBTuple):
            return obj

        if isinstance(obj, cls):
            return obj.rgb

        for cspace, ctype in COLORSPACES.items():
            if isinstance(obj, ctype):
                converter = getattr(convert, f"{cspace}2rgb", None)
                if converter:
                    return converter(obj)

        if isinstance(obj, tuple):
            if (
                isinstance(obj[0], (int, float))
                and isinstance(obj[1], (int, float))
                and isinstance(obj[2], (int, float))
            ):
                if abs(obj[0]) > 1 or abs(obj[1]) > 1 or abs(obj[2]) > 1:
                    return RGBTuple(*tuple((abs(o) % 256) / 255 for o in obj))
                else:
                    return RGBTuple(*tuple(abs(o) for o in obj))

        # use the hash
        try:
            hsh = hash(obj)
        except TypeError:
            hsh = hash(str(obj))

        r = hsh % 1e3
        g = int(hsh / 1e3) % 1e3
        b = int(hsh / 1e6) % 1e3

        return RGBTuple(r / 999, g / 999, b / 999)

    @classmethod
    def colorize(cls, obj: Any) -> "Color":
        if isinstance(obj, Color):
            return Color(obj)

        return Color(Color._colorize(obj))

    def set(self, **kwargs):
        return Color(self, **kwargs)

    def lighten(self, amount=10):
        return self.set(cie_l=self.cie_l + amount)

    def darken(self, amount=10):
        return self.set(cie_l=self.cie_l - amount)

    def saturate(self, amount=10):
        return self.set(cie_c=self.cie_c + amount)

    def desaturate(self, amount=10):
        return self.set(cie_c=max(0, self.cie_c - amount))

    def rotate(self, amount=0.1):
        return self.set(cie_h=self.cie_h + amount)

    def gray(self):
        return Color(LabTuple(self.cie_l, 0, 0))

    def mix(self, color: "Color", ratio: float = 0.5, cspace: str = None, gamma: float = None) -> "Color":
        if cspace is None or cspace not in COLORSPACES:
            cspace = self.cspace

        if gamma is None:
            gamma = 1.0

        ratio = min(abs(ratio), 1)
        prop1, prop2 = getattr(self, cspace), getattr(color, cspace)

        huep = hueprop(cspace)
        newprop = prop1.__class__(
            *tuple(
                ops.mix_linear(v1, v2, ratio, gamma)
                if idx != huep
                else ops.mix_hue(v1, v2, ratio, gamma)
                for v1, v2, idx in zip(prop1, prop2, range(len(prop1)))
            )
        )
        alpha = self.alpha * (1 - ratio) + color.alpha * ratio
        return Color(newprop, alpha=alpha, cspace=self.cspace)

    def closest_named(self, num: int = 3) -> List["Color"]:
        # TODO return closest named colors
        return []

    def distance(self, other: "Color") -> float:
        return distance.distance_cie94(self.lab, other.lab)

    def complementary(self, cspace: "str" = None):
        if cspace is None:
            cspace = self.cspace

        return ops.sub(Color("#fff"), self, cspace)

    def _divide_wheel(self, n: int, cspace: "str" = None):
        if cspace is None:
            cspace = self.cspace

        if cspace in ["rgb", "hsl", "hsv", "hwb"]:
            return [self.set(hue=self.hue + v / n) for v in range(n)]

        if cspace in ["lab", "lch", "xyz"]:
            return [self.set(cie_h=self.cie_h + v / n) for v in range(n)]

    def triad(self, cspace: "str" = None):
        return self._divide_wheel(3, cspace)

    def square(self, cspace: "str" = None):
        return self._divide_wheel(4, cspace)

    def tetrad(self, cspace: "str" = None):
        colors = self._divide_wheel(6, cspace)
        return colors[0:2] + colors[3:5]

    def split_complementary(self, cspace: "str" = None):
        colors = self._divide_wheel(12, cspace)
        return colors[0:1] + colors[5:6] + colors[7:8]

    def analogous(self, cspace: "str" = None):
        colors = self._divide_wheel(12, cspace)
        return [colors[-1]] + colors[0:2]

    def similar(self, other: "Color") -> bool:
        return self.distance(other) < 2.3

    @property
    def name(self):
        if getattr(self, "_name", None) is None:
            self._name = hex2name(self.lhex) or self.hex
        return self._name

    @property
    def rgb(self):
        return ops.normalize_1base(self._rgb)

    @rgb.setter
    def rgb(self, rgb: CTuple):
        if not self._initialized:
            self._rgb = RGBTuple(*rgb)  # NOT normalized
            hue = self.hue
            self._hsl = ops.normalize_huebase(convert.rgb2hsl(ops.normalize_1base(self._rgb)))  # type: ignore
            if self._hsl.saturation == 0:
                self._hsl = HSLTuple(hue, self._hsl.saturation, self._hsl.lightness)
        else:
            raise TypeError("Should not modify an existing 'Color' instance")

    @property
    def clipped(self):
        return self.rgb != self._rgb

    @property
    def rgb256(self):
        if getattr(self, "_rgb256", None) is None:
            hx = convert.rgb2hex(self.rgb, True)[1:]
            self._rgb256 = RGBTuple(
                *tuple(int(hx[v * 2 : v * 2 + 2], 16) for v in range(3))
            )
        return self._rgb256

    @rgb256.setter
    def rgb256(self, rgb: CTuple):
        self.rgb = ops.normalize_1base(RGBTuple(*tuple(c / 255 for c in rgb)))
        self._rgb256 = rgb

    @property
    def hsl(self):
        return self._hsl

    @hsl.setter
    def hsl(self, hsl: CTuple):
        if not self._initialized:
            self._hsl = ops.normalize_huebase(HSLTuple(*hsl))  # type: ignore
            self._rgb = convert.hsl2rgb(self._hsl)
        else:
            raise TypeError("Should not modify an existing 'Color' instance")

    @property
    def luminance(self):
        # should be the same as y in 'xyz'
        if getattr(self, "_luminance", None) is None:
            rgb = self.rgb
            rgb_lum = tuple(
                c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb
            )
            self._luminance = (
                0.2126 * rgb_lum[0] + 0.7152 * rgb_lum[1] + 0.0722 * rgb_lum[2]
            )

        return self._luminance

    @property
    def lhexa(self):
        """Hexadecimal notation with alpha
        """
        ha = f"{int(self.alpha * 255):02x}"
        return self.lhex + ha

    @property
    def hexa(self):
        ha = f"{int(self.alpha * 255):02x}"
        if ha[0] == ha[1] and len(self.hex) == 4:
            return self.hex + ha[0]

        return self.lhex + ha

    @property
    def lhex(self):
        if getattr(self, "_lhex", None) is None:
            self._lhex = convert.rgb2hex(self.rgb, True)
        return self._lhex

    @property
    def cssrgb(self):
        if getattr(self, "_cssrgb", None) is None:
            rgb256 = self.rgb256
            if self.alpha == 1:
                self._cssrgb = f"rgb({rgb256.red}, {rgb256.green}, {rgb256.blue})"
            else:
                self._cssrgb = f"rgba({rgb256.red}, {rgb256.green}, {rgb256.blue}, {self.alpha:.5g})"

        return self._cssrgb

    @property
    def csshsl(self):
        if getattr(self, "_csshsl", None) is None:
            sat = int(self.saturation * 1000) / 10
            lig = int(self.lightness * 1000) / 10
            if self.alpha == 1:
                self._csshsl = f"hsl({int(360 * self.hue)}, {sat:.4g}%, {lig:.4g}%)"
            else:
                self._csshsl = f"hsla({int(360 * self.hue)}, {sat:.4g}%, {lig:.4g}%, {self.alpha:.5g})"
        return self._csshsl

    @property
    def csshwb(self):
        if getattr(self, "_csshwb", None) is None:
            white = int(self.whiteness * 1000) / 10
            black = int(self.blackness * 1000) / 10
            if self.alpha == 1:
                self._csshwb = f"hwb({int(360 * self.hue)}deg {white:.4g}% {black:.4g}%)"
            else:
                self._csshwb = f"hwb({int(360 * self.hue)}deg {white:.4g}% {black:.4g}% / {self.alpha:.5g})"

        return self._csshwb

    @property
    def csslab(self):
        if getattr(self, "_csslab", None) is None:
            ciel = int(self.cie_l * 100) / 100
            ciea = int(self.cie_a * 100) / 100
            cieb = int(self.cie_b * 100) / 100
            if self.alpha == 1:
                self._csslab = f"lab({ciel:.4g}% {ciea:.4g} {cieb:.4g})"
            else:
                self._csslab = f"lab({ciel:.4g}% {ciea:.4g} {cieb:.4g} / {self.alpha:.5g})"

        return self._csslab

    @property
    def csslch(self):
        if getattr(self, "_csslch", None) is None:
            ciel = int(self.cie_l * 100) / 100
            ciec = int(self.cie_c * 100) / 100
            if self.alpha == 1:
                self._csslch = f"lch({ciel:.4g}% {ciec:.4g} {int(360 * self.cie_h)}deg)"
            else:
                self._csslch = f"lch({ciel:.4g}% {ciec:.4g} {int(360 * self.cie_h)}deg / {self.alpha:.5g})"

        return self._csslch

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        if not self._initialized:
            alpha = abs(value)
            self._alpha = alpha if alpha <= 1 else (alpha % 256) / 255
        else:
            raise TypeError("Should not modify an existing 'Color' instance")

    @property
    def pltc(self):
        """matplotlib color tuple"""
        return self.rgb + (self.alpha,)

    def contrast_ratio(self, other: "Color") -> float:
        """WCAG relative contrast ratio

        contrast_ratio > 4.5:1 - AA
        contrast_ratio > 7:1 - AAA
        """
        l1, l2 = self.luminance, other.luminance
        if l2 > l1:
            l1, l2 = l2, l1

        return (l1 + 0.05) / (l2 + 0.05)

    def __str__(self):
        return self.hex

    def __repr__(self):
        return f"<Color {self.name} - {self.csshsl}>"

    def __eq__(self, other):
        if isinstance(other, Color):
            return self._eq(self, other)

        return NotImplemented

    def __add__(self, other):
        if isinstance(other, (Color, tuple, float, int)):
            return ops.add(self, other)

        raise TypeError(f"Cannot add '{type(other)}' to 'Color'")

    def __sub__(self, other):
        if isinstance(other, (Color, tuple, float, int)):
            return ops.sub(self, other)

        raise TypeError(f"Cannot substract '{type(other)}' from 'Color'")

    def __mul__(self, other):
        if isinstance(other, (Color, tuple, float, int)):
            return ops.mul(self, other)

        raise TypeError(f"Cannot multiply '{type(other)}' with 'Color'")

    def __truediv__(self, other):
        if isinstance(other, (Color, tuple, float, int)):
            return ops.div(self, other)

        raise TypeError(f"Cannot multiply '{type(other)}' with 'Color'")

    def __radd__(self, color):
        return self + color

    def __rmul__(self, color):
        return self * color

    def __hash__(self):
        hsl = self.hsl
        return int(
            int(hsl.hue * 3.6e3) * 1e9
            + int(hsl.saturation * 1e3) * 1e6
            + int(hsl.lightness * 1e3) * 1e3
            + int(self.alpha * 1e3)
        )

    @property
    def textcolor(self):
        if getattr(self, "_textcolor", None) is None:
            w = Color("#fff")
            b = Color("#000")
            ctrw = self.contrast_ratio(w)
            ctrb = self.contrast_ratio(b)
            if ctrw > ctrb:
                self._textcolor = w
            else:
                self._textcolor = b

        return self._textcolor

    @property
    def termbg(self):
        rgb = self.rgb256
        return f"\x1b[48;2;{rgb.red};{rgb.green};{rgb.blue}m"

    @property
    def termfg(self):
        rgb = self.rgb256
        return f"\x1b[38;2;{rgb.red};{rgb.green};{rgb.blue}m"

    def _displayimage(
        self,
        width: int = None,
        height: int = None,
        border: int = None,
        bgcolors: List["Color"] = None,
    ) -> List[List["Color"]]:
        if width is None:
            width = self.DISPLAY_WIDTH
        if height is None:
            height = self.DISPLAY_HEIGHT
        if border is None:
            border = self.DISPLAY_BORDER

        w = width + 2 * border
        h = height + 2 * border
        img = []

        if bgcolors is None:
            bgcolors = getattr(
                self, "bgcolors", [Color(LabTuple(95, 0, 0)), Color(LabTuple(65, 0, 0))]
            )

        bgl = len(bgcolors)

        for y in range(h):
            line = []
            for x in range(w):
                bgc = bgcolors[(y + x) % bgl]
                if x < border or y < border or x > w - border - 1 or y > h - border - 1:
                    line.append(bgc)
                elif y < w / 2:
                    line.append(blend.blend(self, bgc))
                elif x < w / 2:
                    line.append(blend.blend(self, bgc, gamma=1))
                else:
                    line.append(self.set(alpha=1))
            img.append(line)

        return img

    @property
    def displayimage(self) -> List[List["Color"]]:
        return self._displayimage()

    @property
    def termimage(self) -> str:
        return terminal.draw(self.displayimage)

    @property
    def info(self):
        info = [
            self.lhex if self.lhex == self.name else f"{self.name} - {self.lhex}",
            self.cssrgb,
            self.csshsl,
            self.csslab,
        ]

        return "\n".join(info) + "\n"

    @property
    def display(self):
        timg = self.termimage
        info = self.info
        output = ["\n"]
        for timgl, infol in zip_longest(timg.split("\n"), info.split("\n")):
            output.append("  ")
            output.append(timgl or "")
            output.append("  ")
            output.append(infol or "")
            output.append("  \n")

        return "".join(output)

    @property
    def hexdisplay(self):
        return f"{self.termbg}{self.textcolor.termfg} {self.lhex} {self.termreset}"

    def print(self, fmt: str = "display", force_ansi: bool = False, stream = sys.stdout):
        if not force_ansi and not sys.stdout.isatty() and fmt in ["display", "hexdisplay"]:
            fmt = "lhex"

        content = getattr(self, fmt, self.lhex)
        print(content, file=stream)
