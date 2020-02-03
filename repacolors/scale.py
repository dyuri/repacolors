from .colors import Color
from .types import LabTuple
from .blend import blend
from typing import List, Any, Tuple, Callable
from . import terminal
import math


def _binomial(i: int, n: int) -> float:
    """Binomial coefficient
    """
    return math.factorial(n) / float(math.factorial(i) * math.factorial(n - i))


def _bernstein(t: float, i: int, n: int) -> float:
    """Bernstein polynom
    """
    return _binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))


def _bezier(
    points: List[Tuple[float, ...]], t: float, gamma: float = 1.0
) -> Tuple[float, ...]:
    """Calculate coordinate of a point in the bezier curve
    """
    n = len(points) - 1
    val = [0.0 for _ in range(len(points[0]))]
    for i, pos in enumerate(points):
        bern = _bernstein(t, i, n)
        val = [v + (p * bern) ** gamma for v, p in zip(val, pos)]

    return tuple(val)


def bezier_ip(
    colors: List[Color], pos: float = 0.5, cspace: str = "lab", gamma: float = 1.0
) -> Color:
    ctup = _bezier([getattr(c, cspace) for c in colors], pos, gamma)
    alpha = _bezier([(c.alpha,) for c in colors], pos)[0]
    cargs = {cspace: ctup, "alpha": min(1.0, alpha)}

    return Color(**cargs)  # type: ignore


def linear_ip(
    colors: List[Color], pos: float = 0.5, cspace: str = "lab", gamma: float = 1.0
) -> Color:

    lenc = len(colors)
    idx = int(pos * (lenc - 1))
    col1, col2 = colors[idx : idx + 2]
    ratio = (pos - idx / (lenc - 1)) * (lenc - 1)

    return col1.mix(col2, ratio=ratio, cspace=cspace, gamma=gamma)


def project_domain(pos: float, domain: List[float]) -> float:
    """Project position of `pos` in `domain` into [0, 1] range
    """

    reverse = False
    if domain[0] > domain[-1]:
        # reverse
        domain = list(reversed(domain))
        reverse = True

    if pos <= domain[0]:
        return 0 if not reverse else 1
    if pos >= domain[-1]:
        return 1 if not reverse else 0

    lend = len(domain)
    prev = (0.0, 0.0)
    for posx, domx in enumerate(domain):
        curr = (posx / (lend - 1), domx)
        if pos <= domx:
            break
        prev = curr

    value = (pos - prev[1]) / (curr[1] - prev[1]) * (curr[0] - prev[0]) + prev[0]

    return value if not reverse else 1 - value


class ColorScale:
    """Maps numeric values to a color palette
    """

    DISPLAY_BORDER = 1
    DISPLAY_HEIGHT = 4
    DISPLAY_WIDTH = 20
    INTERPOLATORS = {
        "linear": linear_ip,
        "bezier": bezier_ip,
    }

    def __init__(
        self,
        colors: List[Any] = [Color("#ffffff"), Color("#000000")],
        domain: List[float] = None,
        gamma: float = 1.0,
        cspace: str = "lab",
        gamma_correction: float = None,
        interpolator: str = "linear",
    ):

        # convert 'colors' to list of Colors
        self.colors = [c if isinstance(c, Color) else Color(c) for c in colors]
        self.domain: List[float] = [0, 1] if domain is None else domain
        self.gamma = gamma
        self.cspace = cspace
        self.interpolator = self.INTERPOLATORS.get(interpolator, linear_ip)

        if gamma_correction is None:
            if (
                cspace in ["rgb", "hsl", "hsv", "hwb"]
                and self.interpolator != bezier_ip
            ):
                gamma_correction = 2.2
            else:
                gamma_correction = 1.0

        self.gamma_correction = gamma_correction

    @property
    def reversed(self):
        return self.domain[0] > self.domain[-1]

    def reverse(self):
        self.domain.reverse()

    def __getitem__(self, key):
        if isinstance(key, (float, int)):
            return self._get_color_for_pos(key)

    def _get_color_for_pos(self, pos: float) -> Color:
        projpos = project_domain(pos, self.domain)

        if self.gamma != 1.0:
            projpos = projpos ** self.gamma

        colors = self.colors if not self.reversed else list(reversed(self.colors))

        if projpos == 0:
            return colors[0]
        if projpos == 1:
            return colors[-1]

        return Color(
            self.interpolator(self.colors, projpos, self.cspace, self.gamma_correction)
        )

    def _displayimage(
        self,
        width: int = None,
        height: int = None,
        border: int = None,
        bgcolors: List["Color"] = None,
    ) -> List[List["Color"]]:
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
            bgcolors = getattr(
                self, "bgcolors", [Color(LabTuple(95, 0, 0)), Color(LabTuple(65, 0, 0))]
            )

        bgl = len(bgcolors)

        for y in range(h):
            line = []
            for x in range(w):
                bgc = bgcolors[(y + x) % bgl]
                if x < border or y < border or x > w - border - 1 or y > h - border - 1:
                    line.append(bgc)
                else:
                    line.append(
                        blend(
                            self[
                                self.domain[0]
                                + (self.domain[-1] - self.domain[0])
                                * (x - border)
                                / width
                            ],
                            bgc,
                        )
                    )

            img.append(line)

        return img

    @property
    def displayimage(self) -> List[List[Color]]:
        return self._displayimage()

    @property
    def termimage(self) -> str:
        return terminal.draw(self.displayimage)

    def print(
        self,
        width: int = None,
        height: int = None,
        border: int = None,
        bgcolors: List["Color"] = None,
    ):
        print(terminal.draw(self._displayimage(width, height, border, bgcolors)))
