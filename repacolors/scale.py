from .colors import Color
from .types import LabTuple
from .blend import blend
from typing import List
from . import terminal


class ColorScale():
    """Maps numeric values to a color palette
    """

    DISPLAY_BORDER = 1
    DISPLAY_HEIGHT = 4
    DISPLAY_WIDTH = 20

    def __init__(self, colors: List[Color] = [Color("#ffffff"), Color("#000000")], cspace: str = "lab"):
        self.colors = colors
        self.cspace = cspace

    def __getitem__(self, key):
        if isinstance(key, (float, int)):
            return self._get_color_from_pos(key)

    def _get_color_from_pos(self, pos: float) -> Color:
        # TODO
        return self.colors[0].mix(self.colors[1], ratio=pos, cspace=self.cspace)

    def _displayimage(self, width: int = None, height: int = None, border: int = None, bgcolors: List["Color"] = None) -> List[List["Color"]]:
        if width is None:
            width = self.DISPLAY_WIDTH
        if height is None:
            height = self.DISPLAY_HEIGHT
        if border is None:
            border = self.DISPLAY_BORDER

        w = width + 2 * border
        h = height + 2 * border
        img = []

        if bgcolors is None:
            bgcolors = getattr(self, "bgcolors", [Color(LabTuple(95, 0, 0)), Color(LabTuple(65, 0, 0))])

        bgl = len(bgcolors)

        for y in range(h):
            line = []
            for x in range(w):
                bgc = bgcolors[(y + x) % bgl]
                if x < border or y < border or x > w - border - 1 or y > h - border - 1:
                    line.append(bgc)
                else:
                    line.append(blend(self[(x - border) / width], bgc))

            img.append(line)

        return img

    @property
    def displayimage(self) -> List[List[Color]]:
        return self._displayimage()

    @property
    def termimage(self) -> str:
        return terminal.draw(self.displayimage)

    def print(self, width: int = None, height: int = None, border: int = None, bgcolors: List["Color"] = None):
        print(terminal.draw(self._displayimage(width, height, border, bgcolors)))
