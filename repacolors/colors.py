import json
import os
import sys
import math
import re
import subprocess
from itertools import zip_longest
from typing import Dict, Any, Optional, Callable, Iterator, List, Union, Tuple
from . import convert
from . import terminal
from . import distance
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


def equal_hex(c1: "Color", c2: "Color") -> bool:
    return c1.lhex == c2.lhex


def equal_hsl(c1: "Color", c2: "Color") -> bool:
    return c1.csshsl == c2.csshsl


def equal_hsla(c1: "Color", c2: "Color") -> bool:
    return c1.csshsla == c2.csshsla


def equal_hash(c1: "Color", c2: "Color") -> bool:
    return hash(c1) == hash(c2)


def get_cspace(color: Union[CTuple, "Color"]):
    cspace = getattr(color, "cspace", "unknown")
    if isinstance(color, HSLTuple):
        cspace = "hsl"
    elif isinstance(color, RGBTuple):
        cspace = "rgb"
    elif isinstance(color, HSVTuple):
        cspace = "hsv"
    elif isinstance(color, HWBTuple):
        cspace = "hwb"
    elif isinstance(color, YUVTuple):
        cspace = "yuv"
    elif isinstance(color, XYZTuple):
        cspace = "xyz"
    elif isinstance(color, LabTuple):
        cspace = "lab"
    elif isinstance(color, LChTuple):
        cspace = "lch"
    elif isinstance(color, CMYKTuple):
        cspace = "cmyk"

    return cspace


def normalize_1base(c: CTuple) -> CTuple:
    cls = c.__class__
    return cls(*tuple(min(max(v, 0), 1) for v in c))  # type: ignore


def normalize_huebase(c: CTuple) -> CTuple:
    cls = c.__class__
    return cls(1 if c[0] == 1 else c[0] % 1, *tuple(min(max(v, 0), 1) for v in c[1:3]))  # type: ignore


def normalize_lab(c: CTuple) -> LabTuple:
    return LabTuple(min(max(c[0], 0), 400), *tuple(min(max(v, -160), 160) for v in c[1:3]))


def normalize_lch(c: CTuple) -> LChTuple:
    return LChTuple(min(max(c[0], 0), 400), min(abs(c[1]), 230), 1 if c[2] == 1 else c[2] % 1)


def normalize(color: CTuple, cspace: str = None) -> CTuple:
    cspace = cspace if cspace else get_cspace(color)

    # TODO hsv, hwb
    if cspace in ["rgb", "yuv", "xyz", "cmyk"]:
        return normalize_1base(color)
    elif cspace in ["hsl", "hsv", "hwb"]:
        return normalize_huebase(color)
    elif cspace == "lab":
        return normalize_lab(color)
    elif cspace == "lch":
        return normalize_lch(color)

    return color


def mul_f(t: CTuple, n: float) -> CTuple:
    cls = t.__class__
    return cls(*tuple(v * n for v in t))  # type: ignore


# TODO refactor with add
def mul(color1: "Color", color2: Union["Color", CTuple], cspace: str = None) -> "Color":
    if cspace is None:
        if isinstance(color2, Color):
            cspace = color1.cspace
        else:
            cspace = get_cspace(color2)

    ctup1 = getattr(color1, cspace)
    ctup2 = getattr(color2, cspace) if isinstance(color2, Color) else color2
    cls = ctup1.__class__

    ctup = normalize(cls(*tuple(p1 * p2 for p1, p2 in zip(ctup1, ctup2))))
    return Color(ctup)


def add(color1: "Color", color2: Union["Color", CTuple], cspace: str = None) -> "Color":
    if cspace is None:
        if isinstance(color2, Color):
            cspace = color1.cspace
        else:
            cspace = get_cspace(color2)

    ctup1 = getattr(color1, cspace)
    ctup2 = getattr(color2, cspace) if isinstance(color2, Color) else color2
    cls = ctup1.__class__

    ctup = normalize(cls(*tuple(p1 + p2 for p1, p2 in zip(ctup1, ctup2))))
    return Color(ctup)


def gradient(
    frm: "Color", to: "Color", steps: int = 10, prop: str = "hsl"
) -> Iterator["Color"]:
    if steps < 2:
        raise ValueError(f"Gradient steps should be more than 1 ({steps})")

    prp = "hsl" if prop == "hsl:long" else prop
    p1, p2 = getattr(frm, prp), getattr(to, prp)
    cls = p1.__class__

    # HSL direction - short vs long
    if prop == "hsl" and abs(p1[0] - p2[0]) > 0.5:
        p1 = HSLTuple(p1[0] - 1.0, p1[1], p1[2])
    elif prop == "hsl:long" and abs(p1[0] - p2[0]) < 0.5:
        p2 = HSLTuple(p2[0] - 1.0, p2[1], p2[2])

    deltac = cls(*tuple((p[1] - p[0]) / (steps - 1) for p in zip(p1, p2)))

    return (frm + mul_f(deltac, i) for i in range(steps))


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
        color[cspace] = getattr(convert, f"rgb2{cspace}")(
            RGBTuple(*color["rgb"])
        )

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
            privattr = convertfn(obj.rgb)
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
        equality: Optional[Callable[["Color", "Color"], bool]] = None,
        **kwargs,
    ):
        self._hsl = HSLTuple(0, 0, 0)
        self._rgb = RGBTuple(0, 0, 0)
        self._alpha = 1  # TODO better alpha support
        self.cspace = "hsl"

        self._initialized = False

        self._eq = equality if equality is not None else equal_hex

        # from color
        if isinstance(colordef, Color):
            self.hsl = colordef.hsl
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
                self.alpha = int(colordef[8:9], 16) / 255
        elif colordef.startswith("rgb") or colordef.startswith("hsl") or colordef.startswith("hwb"):
            mode = colordef[:3]
            clr, self.alpha = self.parse_css_color_values(colordef, mode)
            setattr(self, mode, clr)
            self.cspace = mode
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
    def parse_css_color_values(csscolordef: str, mode: str = "rgb") -> Tuple[CTuple, float]:
        """Parse CSS color definition

        https://developer.mozilla.org/en-US/docs/Web/CSS/color_value
        """
        begin = csscolordef.index("(")
        end = csscolordef.index(")")
        cnt = csscolordef[begin + 1:end]
        alpha = 1.0

        if "," in cnt:
            cnt = re.sub(r"\s+", " ", cnt)
            values = [v.strip() for v in cnt.split(",")]
        else:
            cnt = cnt.replace("/", " ")
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

        # rgb
        return float(csscolorvalue) / 255

    @classmethod
    def pick(cls, picker: Union[str, List[str]] = "xcolor") -> "Color":
        proc = subprocess.Popen(picker, stdout=subprocess.PIPE)
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

    def lighten(self, amount=.1):
        return self.set(lightness=self.lightness + amount)

    def darken(self, amount=.1):
        return self.set(lightness=self.lightness - amount)

    def saturate(self, amount=.1):
        return self.set(saturation=self.saturation + amount)

    def desaturate(self, amount=.1):
        return self.set(saturation=self.saturation - amount)

    def rotate(self, amount=.1):
        return self.set(hue=self.hue + amount)

    def gradient(
        self, to: "Color", steps: int = 10, cspace: str = None
    ) -> Iterator["Color"]:
        if cspace is None:
            cspace = self.cspace
        return gradient(self, to, steps, cspace)

    def blend(self, color: "Color", prop: str = None) -> "Color":
        if prop is None:
            prop = self.cspace
        prop1 = getattr(self, prop)
        prop2 = getattr(color, prop)
        newprop = prop1.__class__(*tuple((v1 + v2) / 2 for v1, v2 in zip(prop1, prop2)))
        return Color(newprop, cspace=self.cspace)

    def closest_named(self, num: int = 3) -> List["Color"]:
        # TODO return closest named colors
        return []

    def distance(self, other: "Color") -> float:
        return distance.distance_cie94(self.lab, other.lab)

    def similar(self, other: "Color") -> bool:
        return self.distance(other) < 2.3

    @property
    def name(self):
        if getattr(self, "_name", None) is None:
            self._name = hex2name(self.lhex) or self.hex
        return self._name

    @property
    def rgb(self):
        return self._rgb

    @rgb.setter
    def rgb(self, rgb: CTuple):
        if not self._initialized:
            self._rgb = normalize_1base(RGBTuple(*rgb))  # type: ignore
            hue = self.hue
            self._hsl = convert.rgb2hsl(self._rgb)
            if self._hsl.saturation == 0:
                self._hsl = HSLTuple(
                    hue, self._hsl.saturation, self._hsl.lightness
                )
        else:
            raise TypeError("Should not modify an existing 'Color' instance")

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
        self.rgb = normalize_1base(RGBTuple(*tuple(c / 255 for c in rgb)))
        self._rgb256 = rgb

    @property
    def hsl(self):
        return self._hsl

    @hsl.setter
    def hsl(self, hsl: CTuple):
        if not self._initialized:
            self._hsl = normalize_huebase(HSLTuple(*hsl))
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

    def contrast_ratio(self, other: "Color") -> float:
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
        if getattr(self, "_lhex", None) is None:
            self._lhex = convert.rgb2hex(self.rgb, True)
        return self._lhex

    @property
    def cssrgb(self):
        if getattr(self, "_cssrgb", None) is None:
            rgb256 = self.rgb256
            self._cssrgb = f"rgb({rgb256.red}, {rgb256.green}, {rgb256.blue})"
        return self._cssrgb

    @property
    def cssrgba(self):
        if getattr(self, "_cssrgba", None) is None:
            rgb256 = self.rgb256
            self._cssrgba = (
                f"rgba({rgb256.red}, {rgb256.green}, {rgb256.blue}, {self.alpha:.5g})"
            )
        return self._cssrgba

    @property
    def csshsl(self):
        if getattr(self, "_csshsl", None) is None:
            self._csshsl = f"hsl({int(360 * self.hue)}, {(100 * self.saturation):.4g}%, {(100 * self.lightness):.4g}%)"
        return self._csshsl

    @property
    def csshsla(self):
        if getattr(self, "_csshsla", None) is None:
            self._csshsla = f"hsla({int(360 * self.hue)}, {(100 * self.saturation):.4g}%, {(100 * self.lightness):.4g}%, {self.alpha:.5g})"
        return self._csshsla

    @property
    def csshwb(self):
        if getattr(self, "_csshwb", None) is None:
            self._csshwb = f"hwb({int(360 * self.hue)}, {(100 * self.whiteness):.4g}%, {(100 * self.blackness):.4g}%)"
        return self._csshwb

    @property
    def csshwba(self):
        if getattr(self, "_csshwba", None) is None:
            self._csshwba = f"hwb({int(360 * self.hue)}, {(100 * self.whiteness):.4g}%, {(100 * self.blackness):.4g}%, {self.alpha:.5g})"
        return self._csshwba

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

    def __str__(self):
        return self.hex

    def __repr__(self):
        return f"<Color {self.name} - {self.csshsla}>"

    def __eq__(self, other):
        if isinstance(other, Color):
            return self._eq(self, other)

        return NotImplemented

    def __add__(self, other):
        if isinstance(other, (Color, tuple)):
            return add(self, other)

        raise TypeError(f"Cannot add '{type(other)}' to 'Color'")

    # TODO see __add__
    def __sub__(self, other):
        if not isinstance(other, Color):
            raise TypeError(f"Cannot substract '{type(other)}' from 'Color'")

        hsl = tuple(p[0] - p[1] for p in zip(self.hsl, other.hsl))
        return Color(
            hsl=(1 if hsl[0] == 1 else hsl[0] % 1, max(hsl[1], 0), max(hsl[2], 0))
        )

    # TODO
    def __mul__(self, n):
        if not isinstance(n, (int, float)):
            raise TypeError(f"Cannot multiply 'Color' with '{type(n)}'")
        if n < 0:
            raise TypeError("Cannot multiply 'Color' with negative values")

        hsl = tuple(p * n for p in self.hsl)
        return Color(
            hsl=(1 if hsl[0] == 1 else hsl[0] % 1, min(hsl[1], 1), min(hsl[2], 1))
        )

    def __rmul__(self, n):
        return self * n

    def __hash__(self):
        hsl = self.hsl
        return int(
            int(hsl.hue * 3.6e3) * 1e9
            + int(hsl.saturation * 1e3) * 1e6
            + int(hsl.lightness * 1e3) * 1e3
            + int(self.alpha * 1e3)
        )

    @property
    def termbg(self):
        rgb = self.rgb256
        return f"\x1b[48;2;{rgb.red};{rgb.green};{rgb.blue}m"

    @property
    def termfg(self):
        rgb = self.rgb256
        return f"\x1b[38;2;{rgb.red};{rgb.green};{rgb.blue}m"

    @property
    def termimage(self):
        img = [[self] * self.DISPLAY_WIDTH] * self.DISPLAY_HEIGHT
        return terminal.draw(terminal.border(img))

    @property
    def info(self):
        info = [
            self.lhex if self.lhex == self.name else f"{self.name} - {self.lhex}",
            self.cssrgb if self.alpha == 1 else self.cssrgba,
            self.csshsl if self.alpha == 1 else self.csshsla,
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

    def print(self, format: str = "display", force_ansi: bool = False):
        if not force_ansi and not sys.stdout.isatty() and format == "display":
            format = "lhex"

        content = getattr(self, format, self.lhex)
        print(content)
