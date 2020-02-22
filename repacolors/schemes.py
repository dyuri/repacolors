from .palette import get_scale
from .scale import ColorScale
from .colors import Color
from .types import HSLTuple, LChTuple
from typing import Tuple


class ColorWheel:
    """Color wheel
    Colors arranged in a circle, 0-12 range (like on a clock)

    Defaults to classic RYB color wheel
    """

    def __init__(self, scale: ColorScale = None):
        if scale is None:
            scale = get_scale("ryb", cyclic=True)

        self.scale = scale
        self.scale.domain = [0, 12]

    def __getitem__(self, pos: float) -> Color:
        if isinstance(pos, (float, int)):
            pos = pos % 12
            return self.scale[pos]

        return NotImplemented

    def _get_position(self, color: Color) -> float:
        pass  # TODO
        return 0

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

    def complementary(self, color: Color) -> Tuple[Color, Color]:
        """Complementary color
        """
        pos = self._get_position(color)
        return self._complementary(pos)

    def triad(self, color: Color) -> Tuple[Color, Color, Color]:
        """Triad color scheme
        """
        pos = self._get_position(color)
        return self._triad(pos)

    def square(self, color: Color) -> Tuple[Color, Color, Color, Color]:
        """Square color scheme
        """
        pos = self._get_position(color)
        return self._square(pos)

    def tetrad(self, color: Color) -> Tuple[Color, Color, Color, Color]:
        """Tetrad/rectangle color scheme
        """
        pos = self._get_position(color)
        return self._tetrad(pos)

    def split_complementary(self, color: Color) -> Tuple[Color, Color, Color]:
        """Split complementary color scheme
        """
        pos = self._get_position(color)
        return self._split_complementary(pos)

    def analogous(self, color: Color) -> Tuple[Color, Color, Color]:
        """Analogous color scheme
        """
        pos = self._get_position(color)
        return self._analogous(pos)


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

    def __init__(self, cie_l: float = 50, cie_c: float = 75):
        self.cie_l = cie_l
        self.cie_c = cie_c

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

# TODO
# - colorwheel
#   - from scale
#   - by color space - hsl/rgb or lch/lab
# - dedicated color wheels
#   - hsl (rgb)
#   - lch (lab)
#   - ryb
# - complementary
# - triad
# - square
# - tetrad
# - split_complementary
# - analogous
