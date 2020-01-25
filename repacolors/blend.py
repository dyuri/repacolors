from . import colors
from .types import RGBTuple


def _normal(fgv: float, bgv: float):
    return fgv


def _multiply(fgv: float, bgv: float):
    return fgv * bgv

BLEND_MODES = {
    "normal": _normal,
    "multiply": _multiply,
}


def blend(fg: "colors.Color", bg: "colors.Color", mode: str = "normal", gamma: float = None) -> "colors.Color":
    if mode not in BLEND_MODES:
        mode == "normal"

    if mode == "normal":
        if fg.alpha == 1:
            return fg
        elif fg.alpha == 0:
            return bg

    if gamma is None:
        if mode == "normal":
            gamma = 2.2
        else:
            gamma = 1.0

    blendfn = BLEND_MODES[mode]

    blended = RGBTuple(
        *tuple(
            (fg.alpha * blendfn(fgv, bgv) ** gamma + (1 - fg.alpha) * bgv ** gamma) ** (1 / gamma)
            for fgv, bgv in zip(fg.rgb, bg.rgb)
        )
    )

    return colors.Color(blended, bg.alpha)


