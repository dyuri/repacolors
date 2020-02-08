"""
https://en.wikipedia.org/wiki/Blend_modes
"""
from . import colors
from .types import RGBTuple


def _normal(fgv: float, bgv: float) -> float:
    return fgv


def _multiply(fgv: float, bgv: float) -> float:
    return fgv * bgv


def _screen(fgv: float, bgv: float) -> float:
    return 1 - (1 - fgv) * (1 - bgv)


def _overlay(fgv: float, bgv: float) -> float:
    return 2 * fgv * bgv if bgv < 0.5 else 1 - 2 * (1 - fgv) * (1 - bgv)


def _hardlight(fgv: float, bgv: float) -> float:
    return _overlay(bgv, fgv)


def _softlight(fgv: float, bgv: float) -> float:
    if fgv <= .5:
        return bgv - (1 - 2 * fgv) * bgv * (1 - bgv)

    if bgv <= .25:
        return bgv + (2 * fgv - 1) * (((16 * bgv - 12) * bgv + 3) * bgv)

    return bgv + (2 * fgv - 1) * (bgv ** 2 - bgv)


BLEND_MODES = {
    "normal": _normal,
    "multiply": _multiply,
    "screen": _screen,
    "overlay": _overlay,
    "hardlight": _hardlight,
    "hard-light": _hardlight,
    "softlight": _softlight,
    "soft-light": _softlight,
    # ...
}


def blend(fg: "colors.Color", bg: "colors.Color", mode: str = "normal", gamma: float = None) -> "colors.Color":
    if mode not in BLEND_MODES:
        mode = "normal"

    if mode == "normal":
        if fg.alpha == 1:
            return fg

        if fg.alpha == 0:
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
