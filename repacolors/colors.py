import json
import os
from . import convert

DIR = os.path.dirname(os.path.realpath(__file__))
CSSJSON = os.path.join(DIR, "css-color-names.json")

with open(CSSJSON, "r") as f:
    CSSNAME2HEX = json.load(f)

HEX2CSSNAME = dict((hx, name) for name, hx in CSSNAME2HEX.items())

COLORCACHE = {}


def get_color(hx, cspace="rgb"):
    if hx in COLORCACHE:
        color = COLORCACHE[hx]
    else:
        color = {"hex": hx, "rgb": convert.hex2rgb(hx), "name": hex2name(hx)}
        COLORCACHE[hx] = color

    if cspace not in color and hasattr(convert, f"rgb2{cspace}"):
        color[cspace] = getattr(convert, f"rgb2{cspace}")(*color["rgb"])

    return color


def name2hex(name):
    return CSSNAME2HEX.get(name, None)


def hex2name(hx):
    return HEX2CSSNAME.get(hx, None)


def closest(r, g, b, n=3, cspace="rgb"):
    named_colors = HEX2CSSNAME.keys()
    col = (r, g, b)
    chx = convert.rgb2hex(*col, True)
    if cspace != "rgb":
        col = getattr(convert, f"rgb2{cspace}")(*col)
    closests = []

    for nch in named_colors:
        if chx == nch:
            continue
        nc = get_color(nch, cspace)
        distance = convert.distance(col, nc[cspace])
        closests.append({"color": nc, "distance": distance})
        # not the most efficient way, but...
        closests.sort(key=lambda c: c["distance"])
        closests = closests[:n]

    return closests
