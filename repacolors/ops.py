from typing import Iterator, List, Union, Callable
import operator
from . import colors
from .types import *

def equal_hex(c1: "colors.Color", c2: "colors.Color") -> bool:
    return c1.lhex == c2.lhex


def equal_hsl(c1: "colors.Color", c2: "colors.Color") -> bool:
    return colors.Color(c1, 1).csshsl == colors.Color(c2, 1).csshsl


def equal_hsla(c1: "colors.Color", c2: "colors.Color") -> bool:
    return c1.csshsl == c2.csshsl


def equal_hash(c1: "colors.Color", c2: "colors.Color") -> bool:
    return hash(c1) == hash(c2)


def get_cspace(color: Union[CTuple, "colors.Color"]):
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
    return LabTuple(
        min(max(c[0], 0), 400), *tuple(min(max(v, -160), 160) for v in c[1:3])
    )


def normalize_lch(c: CTuple) -> LChTuple:
    return LChTuple(
        min(max(c[0], 0), 400), min(abs(c[1]), 230), 1 if c[2] == 1 else c[2] % 1
    )


def normalize(color: CTuple, cspace: str = None) -> CTuple:
    cspace = cspace if cspace else get_cspace(color)

    if cspace in ["rgb", "yuv", "xyz", "cmyk"]:
        return normalize_1base(color)
    elif cspace == "lab":
        return normalize_lab(color)
    elif cspace == "lch":
        return normalize_lch(color)
    elif hueprop(cspace) == 0:
        return normalize_huebase(color)

    return color


def _apply_f(t: CTuple, f: float, op: Callable[[float, float], float]) -> CTuple:
    cls = t.__class__
    return cls(*tuple(op(v, f) for v in t))  # type: ignore


def _apply(color1: "colors.Color", color2: Union["colors.Color", CTuple, float], op: Callable[[float, float], float], cspace: str = None) -> "colors.Color":
    if cspace is None:
        if isinstance(color2, tuple):
            cspace = get_cspace(color2)
        else:
            cspace = color1.cspace

    ctup1 = getattr(color1, cspace)

    if isinstance(color2, (int, float)):
        return colors.Color(normalize(_apply_f(ctup1, color2, op)))

    ctup2 = getattr(color2, cspace) if isinstance(color2, colors.Color) else color2
    cls = ctup1.__class__

    ctup = normalize(cls(*tuple(op(p1, p2) for p1, p2 in zip(ctup1, ctup2))))
    return colors.Color(ctup)


def add(color1: "colors.Color", color2: Union["colors.Color", CTuple, float], cspace: str = None) -> "colors.Color":
    return _apply(color1, color2, operator.add, cspace)


def sub(color1: "colors.Color", color2: Union["colors.Color", CTuple, float], cspace: str = None) -> "colors.Color":
    return _apply(color1, color2, operator.sub, cspace)


def mul(color1: "colors.Color", color2: Union["colors.Color", CTuple, float], cspace: str = None) -> "colors.Color":
    return _apply(color1, color2, operator.mul, cspace)


def div(color1: "colors.Color", color2: Union["colors.Color", CTuple, float], cspace: str = None) -> "colors.Color":
    return _apply(color1, color2, operator.truediv, cspace)


def mix_linear(v1: float, v2: float, ratio: float = .5, gamma: float = 1):
    if gamma == 1:
        return (1 - ratio) * v1 + ratio * v2
    return ((1 - ratio) * v1 ** gamma + ratio * v2 ** gamma) ** (1 / gamma)


def mix_hue(v1: float, v2: float, ratio: float = .5, gamma: float = 1):
    if abs(v1 - v2) > .5:
        if v1 < v2:
            v1 += 1
        else:
            v2 += 1

    return mix_linear(v1, v2, ratio, gamma) % 1


def average(
    colorlist: List["colors.Color"], weights: List[float] = [], cspace: str = None
) -> "colors.Color":
    if len(colorlist) < 1:
        return colors.Color()
    elif len(colorlist) == 1:
        return colorlist[0]

    if cspace is None or cspace not in COLORSPACES:
        cspace = colorlist[0].cspace

    lenw, lenc = len(weights), len(colorlist)

    if lenw < lenc:
        weights = weights + [1 for _ in range(lenc - lenw)]
    elif lenw > lenc:
        weights = weights[:lenc]

    sw = sum(weights)
    weights = [w / sw for w in weights]

    cls = getattr(colorlist[0], cspace).__class__
    retp = cls()
    propnum = len(retp)
    alpha = 0

    for c, w in zip(colorlist, weights):
        cprop = getattr(c, cspace)
        retp = tuple(retp[i] + cprop[i] * w for i in range(propnum))
        alpha += c.alpha * w

    return colors.Color(cls(*retp), alpha=alpha, cspace=cspace)
