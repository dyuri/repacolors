"""Named tuples for color spaces
"""

from typing import Tuple, NamedTuple, Optional

CTuple = Tuple[float, ...]


class HSLTuple(NamedTuple):
    hue: float = 0
    saturation: float = 0
    lightness: float = 0


class RGBTuple(NamedTuple):
    red: float = 0
    green: float = 0
    blue: float = 0


class HSVTuple(NamedTuple):
    hue: float = 0
    saturation: float = 0
    value: float = 0


class HWBTuple(NamedTuple):
    hue: float = 0
    whiteness: float = 0
    blackness: float = 0


class YUVTuple(NamedTuple):
    y: float = 0
    u: float = 0
    v: float = 0


class XYZTuple(NamedTuple):
    x: float = 0
    y: float = 0
    z: float = 0


class LabTuple(NamedTuple):
    l: float = 0
    a: float = 0
    b: float = 0


class LChTuple(NamedTuple):
    l: float = 0
    c: float = 0
    h: float = 0


class CMYKTuple(NamedTuple):
    c: float = 0
    m: float = 0
    y: float = 0
    k: float = 0


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


def hueprop(cspace: str) -> Optional[int]:
    if 'h' in cspace:
        return cspace.index('h')
    return None
