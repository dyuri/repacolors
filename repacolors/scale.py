from .colors import Color
from .types import LabTuple
from .blend import blend
from typing import List, Any
from . import terminal


def project_domain(pos: float, domain: List[float]) -> float:
    """Project position of `pos` in `domain` into [0, 1] range
    """

    if pos <= domain[0]:
        return 0
    if pos >= domain[-1]:
        return 1

    lend = len(domain)
    prev = (0.0, 0.0)
    for posx, domx in enumerate(domain):
        curr = (posx / (lend - 1), domx)
        if pos <= domx:
            break
        prev = curr

    return (pos - prev[1]) / (curr[1] - prev[1]) * (curr[0] - prev[0]) + prev[0]


class ColorScale():
    """Maps numeric values to a color palette
    """

    DISPLAY_BORDER = 1
    DISPLAY_HEIGHT = 4
    DISPLAY_WIDTH = 20

    def __init__(self, colors: List[Any] = [Color("#ffffff"), Color("#000000")], domain: List[float] = None, gamma: float = 1.0, cspace: str = "lab"):

        # convert 'colors' to list of Colors
        self.colors = [c if isinstance(c, Color) else Color(c) for c in colors]
        self.domain: List[float] = [0, 1] if domain is None else domain
        self.gamma = gamma
        self.cspace = cspace

    def __getitem__(self, key):
        if isinstance(key, (float, int)):
            return self._get_color_for_pos(key)

    def _get_color_for_pos(self, pos: float) -> Color:
        projpos = project_domain(pos, self.domain)

        if self.gamma != 1.0:
            projpos = projpos ** self.gamma

        if projpos == 0:
            return self.colors[0]
        elif projpos == 1:
            return self.colors[-1]

        lenc = len(self.colors)
        idx = int(projpos * (lenc - 1))

        col1, col2 = self.colors[idx:idx+2]
        ratio = (projpos - idx / (lenc - 1)) * (lenc - 1)
        return col1.mix(col2, ratio=ratio, cspace=self.cspace)

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
                    line.append(blend(self[self.domain[0] + self.domain[-1] * (x - border) / width], bgc))

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
