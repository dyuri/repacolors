"""Color distance functions
"""

import math
from .types import *

# weighting factors
Wgraphic = (1, 0.045, 0.015)
Wtextile = (2, 0.048, 0.014)


def distance(c1: CTuple, c2: CTuple) -> float:
    """Color distance - eucledian
    Can be used with RGB or CIE-Lab values (CIE76)
    https://en.wikipedia.org/wiki/Color_difference#CIELAB_%CE%94E*

    For Lab colors: diff ~ 2.3 - just noticeable difference
    """

    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def distance_cie94(lab1: LabTuple, lab2: LabTuple, w: Tuple[float, float, float] = Wgraphic) -> float:
    """Color distance - CIE94
    https://en.wikipedia.org/wiki/Color_difference#CIE94
    """

    dL = lab1.l - lab2.l
    c1 = (lab1.a ** 2 + lab1.b ** 2) ** .5
    c2 = (lab2.a ** 2 + lab2.b ** 2) ** .5
    dC = c1 - c2
    dH2 = (lab1.a - lab2.a) ** 2 + (lab1.b - lab2.b) ** 2 - dC ** 2
    dH = 0 if dH2 <= 0 else dH2 ** .5
    sC = 1 + w[1] * c1
    sH = 1 + w[2] * c1

    return ((dL / w[0]) ** 2 + (dC / sC) ** 2 + (dH / sH) ** 2) ** .5
