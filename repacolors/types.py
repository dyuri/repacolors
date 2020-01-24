"""Named tuples for color spaces
"""

from typing import Tuple, NamedTuple

CTuple = Tuple[float, ...]


class HSLTuple(NamedTuple):
    hue: float
    saturation: float
    lightness: float


class RGBTuple(NamedTuple):
    red: float
    green: float
    blue: float


class HSVTuple(NamedTuple):
    hue: float
    saturation: float
    value: float


class HWBTuple(NamedTuple):
    hue: float
    whiteness: float
    blackness: float


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


class LChTuple(NamedTuple):
    l: float
    c: float
    h: float


class CMYKTuple(NamedTuple):
    c: float
    m: float
    y: float
    k: float


COLORSPACES = {
    "rgb": RGBTuple,
    "hsl": HSLTuple,
    "hsv": HSVTuple,
    "hwb": HWBTuple,
    "lab": LabTuple,
    "lch": LChTuple,
    "xyz": XYZTuple,
    "yuv": YUVTuple,
    "cmyk": CMYKTuple,
}
