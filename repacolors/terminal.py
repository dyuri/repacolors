from typing import Iterable, Any, Union, List
from itertools import zip_longest
import shutil


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


def termsize():
    return shutil.get_terminal_size((80, 20))


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
        output.append(TerminalColor.termreset)
        output.append("\n")

    return "".join(output)
