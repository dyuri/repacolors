from typing import Iterator, List, Union
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
def mul(color1: "colors.Color", color2: Union["colors.Color", CTuple], cspace: str = None) -> "colors.Color":
    if cspace is None:
        if isinstance(color2, colors.Color):
            cspace = color1.cspace
        else:
            cspace = get_cspace(color2)

    ctup1 = getattr(color1, cspace)
    ctup2 = getattr(color2, cspace) if isinstance(color2, colors.Color) else color2
    cls = ctup1.__class__

    ctup = normalize(cls(*tuple(p1 * p2 for p1, p2 in zip(ctup1, ctup2))))
    return colors.Color(ctup)


def add(color1: "colors.Color", color2: Union["colors.Color", CTuple], cspace: str = None) -> "colors.Color":
    if cspace is None:
        if isinstance(color2, colors.Color):
            cspace = color1.cspace
        else:
            cspace = get_cspace(color2)

    ctup1 = getattr(color1, cspace)
    ctup2 = getattr(color2, cspace) if isinstance(color2, colors.Color) else color2
    cls = ctup1.__class__

    ctup = normalize(cls(*tuple(p1 + p2 for p1, p2 in zip(ctup1, ctup2))))
    return colors.Color(ctup)


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


# TODO -> scale
def gradient(
    frm: "colors.Color", to: "colors.Color", steps: int = 10, prop: str = "hsl"
) -> Iterator["colors.Color"]:
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
