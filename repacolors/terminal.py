from typing import Iterable, Any, Union, List
from itertools import zip_longest


def _linepairs(image: Iterable[Iterable[Any]]):
    i = iter(image)
    return zip_longest(i, i)


class TerminalColor():
    """Abstract class for terminal pixel
    """

    def __init__(self, color):
        self.color = color

    @property
    def termbg(self):
        return f"\x1b[48;5;{self.color}m"

    @property
    def termfg(self):
        return f"\x1b[38;5;{self.color}m"

    termreset = "\x1b[0m"


def border(
    image: List[List[TerminalColor]],
    border: int = 2,
    bordercolor: Union[TerminalColor, List[TerminalColor]] = None,
) -> Iterable[Iterable[TerminalColor]]:
    if bordercolor is None:
        bordercolor = [TerminalColor(255), TerminalColor(247)]
    if isinstance(bordercolor, TerminalColor):
        bordercolor = [bordercolor]

    tmpimg: List[List[TerminalColor]] = []
    height = len(image)
    width = len(image[0])
    blen = len(bordercolor)

    for y in range(border * 2 + height):
        line: List[TerminalColor] = []
        for x in range(border * 2 + width):
            if x < border or x >= border + width or y < border or y >= border + height:
                line.append(bordercolor[(x + y) % blen])
            else:
                line.append(image[y - border][x - border])
        tmpimg.append(line)

    return tmpimg


def draw(image: Iterable[Iterable[TerminalColor]]) -> str:
    """Draw image (with ANSI escape sequences)

    image - TerminalPixel[][], should be a rectangle
    """
    output = [""]

    linepairs = _linepairs(image)

    for l1, l2 in linepairs:
        if l2 is None:
            l2 = []
        for c1, c2 in zip_longest(l1, l2):
            if c1 and c2:
                output.append(f"{c1.termfg}{c2.termbg}▀")
            elif c1:
                output.append(f"{c1.termfg}▀")
            elif c2:
                output.append(f"{c2.termbg}▀")
            else:
                output.append(" ")
        output.append(TerminalColor.termreset)
        output.append("\n")

    return "".join(output)