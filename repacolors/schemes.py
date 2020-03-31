from .palette import get_scale
from .scale import ColorScale
from .colors import Color
from .types import HSLTuple, LChTuple, LabTuple
from .blend import blend
from .distance import distance_hue
from . import terminal
from typing import Tuple, List
import math


class ColorWheel:
    """Color wheel
    Colors arranged in a circle, 0-12 range (like on a clock)

    Defaults to classic RYB color wheel
    """

    DISPLAY_BORDER = 1

    def __init__(self, scale: ColorScale = None, cspace: str = "rgb"):
        if scale is None:
            scale = get_scale("rybw3", cyclic=True)

        self.scale = scale
        self.cspace = cspace

        # make it cyclic
        if scale.colors[0] != scale.colors[-1]:
            scale.colors.append(scale.colors[0])

        # "around the clock"
        self.scale.domain = [0, 12]

    def __getitem__(self, pos: float) -> Color:
        if isinstance(pos, (float, int)):
            pos = pos % 12
            return self.scale[pos]

        return NotImplemented

    def _get_position(self, color: Color) -> float:
        mindist, minidx, closest = 100.0, 0, color
        colors = self.scale.colors[:-1]

        # search for most similar color (hue) in scale
        for i, col in enumerate(colors):
            dist = abs(distance_hue(color.hue, col.hue))
            if dist < mindist:
                mindist = dist
                minidx = i
                closest = col

        lscale = len(colors)
        pidx, nidx = (minidx - 1) % lscale, (minidx + 1) % lscale
        pcol, ncol = colors[pidx], colors[nidx]
        diff = distance_hue(closest.hue, color.hue)
        pdiff = distance_hue(pcol.hue, color.hue)
        ndiff = distance_hue(ncol.hue, color.hue)

        # different sign of diffs - in between somewhere
        if pdiff * diff < 0:
            idx = minidx - abs(diff / (pdiff - diff))
        elif ndiff * diff < 0:
            idx = minidx + abs(diff / (ndiff - diff))
        else:
            idx = minidx

        return 12 * idx / lscale

    def _adjust(self, color: Color, refcolor: Color) -> Color:
        if self.cspace in ["lab", "lch"]:
            return refcolor.set(cie_h=color.cie_h)

        return refcolor.set(hue=color.hue)

    def _complementary(self, pos: float) -> Tuple[Color, Color]:
        return self[pos], self[pos + 6]

    def _triad(self, pos: float) -> Tuple[Color, Color, Color]:
        return self[pos], self[pos + 4], self[pos + 8]

    def _square(self, pos: float) -> Tuple[Color, Color, Color, Color]:
        return self[pos], self[pos + 3], self[pos + 6], self[pos + 9]

    def _tetrad(self, pos: float) -> Tuple[Color, Color, Color, Color]:
        return self[pos], self[pos + 2], self[pos + 6], self[pos + 8]

    def _split_complementary(self, pos: float) -> Tuple[Color, Color, Color]:
        return self[pos], self[pos + 5], self[pos + 7]

    def _analogous(self, pos: float) -> Tuple[Color, Color, Color]:
        return self[pos], self[pos + 1], self[pos + 11]

    def complementary(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Complementary color
        """
        pos = self._get_position(color)
        colors = self._complementary(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def triad(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Triad color scheme
        """
        pos = self._get_position(color)
        colors = self._triad(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def square(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Square color scheme
        """
        pos = self._get_position(color)
        colors = self._square(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def tetrad(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Tetrad/rectangle color scheme
        """
        pos = self._get_position(color)
        colors = self._tetrad(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def split_complementary(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Split complementary color scheme
        """
        pos = self._get_position(color)
        colors = self._split_complementary(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def analogous(self, color: Color, adjust: bool = True) -> Tuple[Color, ...]:
        """Analogous color scheme
        """
        pos = self._get_position(color)
        colors = self._analogous(pos)
        if not adjust:
            return colors

        return tuple(self._adjust(c, color) for c in colors)

    def monochromatic(self, color: Color, n : int = 5) -> Tuple[Color, ...]:
        """Monochromatic color scheme
        """
        deltal = 1 / n
        diffl = color.lightness % deltal
        lightnesses = [diffl + deltal * i for i in range(n)]
        return tuple(color.set(lightness=lness) for lness in lightnesses)

    def _displayimage(self, width: int = None, border: int = None, bgcolors: List[Color] = None) -> List[List["Color"]]:
        if border is None:
            border = self.DISPLAY_BORDER
        if width is None:
            ts = terminal.termsize()
            width = min(ts[0], ts[1] * 2) - border * 2 - 6 # -6 for prompt

        w = width + 2 * border
        img = []

        if bgcolors is None:
            bgcolors = getattr(
                self, "bgcolors", [Color(LabTuple(35, 0, 0)), Color(LabTuple(5, 0, 0))]
            )

        bgl = len(bgcolors)

        for y in range(w):
            line = []
            for x in range(w):
                bgc = bgcolors[(y + x) % bgl]
                ro, ri = width / 2, width / 3
                rx, ry = w / 2 - x, w / 2 - y
                r = (rx ** 2 + ry ** 2) ** .5
                if r < ro:
                    alpha = math.atan2(ry, rx)
                    pos = 12 * alpha / math.tau - 3
                    alpha = 1
                    if r < ri:
                        alpha = 1 - (ri - r) / ri
                    line.append(blend(self[pos].set(alpha=alpha), bgc))
                else:
                    line.append(bgc)
            img.append(line)

        return img

    def print(
        self,
        width: int = None,
        border: int = None,
        bgcolors: List["Color"] = None,
    ):
        print(terminal.draw(self._displayimage(width, border, bgcolors)))


class HSLColorWheel(ColorWheel):
    """HSL/RGB color wheel
    """

    def __init__(self, lightness: float = .5, saturation: float = 1.0):
        self.lightness = lightness
        self.saturation = saturation

    def __getitem__(self, pos: float) -> Color:
        hue = pos / 12
        return Color(HSLTuple(hue, self.saturation, self.lightness))

    def _get_position(self, color: Color) -> float:
        self.saturation = color.saturation
        self.lightness = color.lightness
        return color.hue * 12


class LChColorWheel(ColorWheel):
    """LCh/Lab color wheel
    """

    def __init__(self, cie_l: float = 60, cie_c: float = 100):
        self.cie_l = cie_l
        self.cie_c = cie_c
        self.cspace = "lab"

    def __getitem__(self, pos: float) -> Color:
        cie_h = pos / 12
        return Color(LChTuple(self.cie_l, self.cie_c, cie_h))

    def _get_position(self, color: Color) -> float:
        self.cie_l = color.cie_l
        self.cie_c = color.cie_c
        return color.cie_h * 12


RYB = ColorWheel()
HSL = HSLColorWheel()
RGB = HSL
LCH = LChColorWheel()
LAB = LCH
