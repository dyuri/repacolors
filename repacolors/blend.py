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


BLEND_MODES = {
    "normal": _normal,
    "multiply": _multiply,
    "screen": _screen,
    "overlay": _overlay,
    "hardlight": _hardlight,
    "hard-light": _hardlight,
    # TODO
}


def blend(fg: "colors.Color", bg: "colors.Color", mode: str = "normal", gamma: float = None) -> "colors.Color":
    if mode not in BLEND_MODES:
        mode = "normal"

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


