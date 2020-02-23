from repacolors import ColorScale
from .colorbrewer import PALETTES as CBPALETTES


PALETTES = {
    "ryb": ["#fe2713", "#fd5307", "#fb9900", "#fabc00", "#fefe34", "#d1e92c", "#66b032", "#0492ce", "#0347fe", "#3e01a4", "#8600af", "#a7194b"],
    "rybw3": ["#FE2712", "#FC600A", "#FB9902", "#FCCC1A", "#FEFE33", "#B2D732", "#66B032", "#347C98", "#0247FE", "#4424D6", "#8601AF", "#C21460"],
    **CBPALETTES
}


def get_palette(name: str):
    if name.lower() not in PALETTES:
        raise KeyError(f"'{name}' palette not found")

    return PALETTES[name.lower()]


def get_scale(name: str, *args, **kwargs) -> ColorScale:
    kwargs["name"] = name
    return ColorScale(get_palette(name), *args, **kwargs)


def demo(width: int = 80):
    for name, colors in PALETTES.items():
        s = ColorScale(colors)
        print(f"{name:12s}", end="")
        s.print(width=width, height=2, border=0)
