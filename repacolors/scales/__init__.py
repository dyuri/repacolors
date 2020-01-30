from repacolors import ColorScale
from .colorbrewer import PALETTES as CBPALETTES


PALETTES = {
    **CBPALETTES
}


def get_scale(name: str, *args, **kwargs) -> ColorScale:
    if name.lower() not in PALETTES:
        raise KeyError(f"'{name}' palette not found")

    return ColorScale(PALETTES[name.lower()], *args, **kwargs)


def demo(width: int = 80):
    for name, colors in PALETTES.items():
        s = ColorScale(colors)
        print(f"{name:12s}", end="")
        s.print(width=width, height=2, border=0)
