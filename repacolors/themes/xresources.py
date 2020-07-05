import os
import xcffib
import xcffib.xproto
from . import Theme


def get(DISPLAY=None, defaults=None):
    """
    Get the X resources
    """

    if DISPLAY is None:
        DISPLAY = os.environ.get("DISPLAY")

    if defaults is None:
        resources = {}
    else:
        resources = defaults.copy()

    try:
        conn = xcffib.connect(display=DISPLAY)
    except xcffib.ConnectionException as err:
        print(err)
        return resources

    root = conn.get_setup().roots[0].root
    atom = conn.core.InternAtom(False, 16, 'RESOURCE_MANAGER').reply().atom

    reply = conn.core.GetProperty(
        False, root, atom, xcffib.xproto.Atom.STRING,
        0, (2 ** 32) - 1).reply()
    conn.disconnect()

    resource_string = reply.value.buf().decode("utf-8")
    resource_list = filter(None, resource_string.split("\n"))

    for resource in resource_list:
        key, value = resource.split(":\t")
        resources[key.strip("*.")] = value

    return resources


_COLOR_PROPS = [f"color{i}" for i in range(16)] + ["background", "foreground"]


def get_colors(DISPLAY=None):
    resources = get(DISPLAY)

    return [resources.get(key, "#000000") for key in _COLOR_PROPS]


def get_theme(DISPLAY=None):
    colors = get_colors(DISPLAY)
    xtheme = Theme(colors, _COLOR_PROPS.copy())

    return xtheme
