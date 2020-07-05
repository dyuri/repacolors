from .theme import Theme

__all__ = ["Theme", "GRUVBOX", "XTHEME"]

GRUVBOX = Theme([
    "#282828", "#cc241d", "#98971a", "#d79921", "#458588", "#b16286", "#689d6a", "#a89984",  # normal
    "#928374", "#fb4934", "#b8bb26", "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#ebdbb2",  # light
    "#fbf1c7", "#9d0006", "#79740e", "#b57614", "#076678", "#8f3f71", "#427b58", "#3c3836",  # dark
    "#1d2021", "#32302f", "#3c3836", "#504945", "#665c54", "#7c6f64",  # b/w - dark
    "#a89984", "#bdae93", "#d5c4a1", "#f2e5bc", "#fbf1c7", "#f9f5d7",  # b/w - light
    "#af3a03", "#d65d0e", "#fe8019",  # oranges
], [
    "black", "red", "green", "yellow", "blue", "purple", "aqua", "lightgray",
    "gray", "lightred", "lightgreen", "lightyellow", "lightblue", "lightpurple", "lightaqua", "white",
    "brightwhite", "darkred", "darkgreen", "darkyellow", "darkblue", "darkpurple", "darkaqua", "darkgray",
    ["b0_h", "background"], "b0_s", "b1", "b2", "b3", "b4",
    "w4", "w3", "w2", ["w0_s", "foreground"], "w0", "w0_h",
    "darkorange", "orange", "lightorange",
])

# try to get XTHEME
XTHEME = GRUVBOX
try:
    from .xresources import get_theme
    XTHEME = get_theme()
except ImportError:
    pass
