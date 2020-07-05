from collections import OrderedDict
from ..colors import Color

DEFAULT_NAMES = [
    "black", "red", "green", "brown", "blue", "magenta", "cyan", "lightgray",
    "darkgray", "lightred", "lightgreen", "yellow", "lightblue", "lightmagenta", "lightcyan", "white",
]

class Theme(OrderedDict):

    def __init__(self, values=None, names=None, aliases=None):
        self._aliases = aliases or {}

        if values is None:
            values = {}
        if isinstance(values, list):
            values = enumerate(values)

        # apply default aliases
        self.apply_ordered_aliases(DEFAULT_NAMES)

        if names is not None:
            self.apply_ordered_aliases(names)

        super().__init__(values)

        self._fgidx = 7
        self._bgidx = 0

    def apply_ordered_aliases(self, names):
        for i, namelist in enumerate(names):
            if not isinstance(namelist, list):
                namelist = [namelist]
            for name in namelist:
                self.alias(name, i)

    @property
    def fg(self):
        if "foreground" in self._aliases:
            return self.foreground
        return self[self._fgidx]

    @property
    def bg(self):
        if "background" in self._aliases:
            return self.background
        return self[self._bgidx]

    def color(self, attr):
        if isinstance(attr, int):
            return Color(self[attr])
        else:
            return Color(getattr(self, attr))

    def display(self):
        output = ["\n"]
        output.append(Color(self.bg).termbg + " " * 8)
        output.append(Color(self.fg).termbg + " " * 8)
        for j in range(2):
            output.append("\n")
            for i in range(8):
                output.append(Color(self[i + j * 8]).termbg + "  ")
        output.append("\n")

        return "".join(output)

    def print(self):
        print(self.display())

    def __getattr__(self, attr):
        attr = self._aliases.get(attr, attr)
        return self[attr]

    def __setattr__(self, attr, value):
        if attr[0] != "_":
            self[attr] = value
        else:
            super().__setattr__(attr, value)

    def alias(self, alias, key):
        self._aliases[alias] = key
