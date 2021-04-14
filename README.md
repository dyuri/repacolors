# repacolors

Small library for color conversion, manipulation, etc.

[![Build Status](https://travis-ci.com/dyuri/repacolors.svg?branch=master)](https://travis-ci.com/dyuri/repacolors)

![demo](./demo.svg)

## Install

```shell
$ pip install repacolors
```

To get the colors from `Xrdb`, install it with the `xextras` extras:

```shell
$ pip install repacolors[xextras]
```

## `repacolor` command

```shell
$ repacolor --help
Usage: repacolor [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  adjust-contrast  Adjust the colors to match required contrast ratio.
  colorwheel       Display colorwheel defined by `name` or created by the...
  display          Display information about the provided colors.
  palette          Get colors of given palette
  pick             Pick colors from your desktop.
  scale            Display color scale defined by the colors provided.
```

### `display`

Display color information in the terminal.

```shell
$ repacolor display red

+--------+ red - #ff0000
|  BIG   | rgb(255, 0, 0)
|  RED   | hsl(0, 100%, 50%)
| SQUARE | lab(53.24% 80.09 67.2)
+--------+

$ repacolor display "#ffaad5" "rgb(128, 12, 46, .8)"
... (displays both colors)
$ echo "#ffffff" | repacolor display
... (displays `white`)
```

### `pick`

Executes color picker and displays the picked color.

```shell
$ repacolor pick
```

The integrated color picker works under _X11/linux_ if installed with *xextras*. If you want to use an external color picker, set the `COLORPICKER` environment variable:

```shell
$ export COLORPICKER=xcolor
$ repacolor pick
```

### `palette`

Display the colors of the palette. If no palette name provided, it shows the palettes available.

```shell
$ repacolor palette
List of available palette names:
ryb, rybw3, orrd, pubu, ...

$ repacolor palette viridis
#440154
#482777
...
```

### `scale`

Display a color scale defined by the input colors.

```shell
$ repacolor scale red white
[colors from red to white]
$ repacolor palette viridis | repacolor scale
[color scale defined by `viridis` colors]
```

### `colorwheel`

Display a color wheel.

Pre defined color wheels:

- `ryb` - The RYB color wheel
- `rgb` or `hsl` - The RGB color wheel
- `lab` or `lch` - CIELAB color wheel

If no color wheel name provided, it will create one from the colors provided on `stdin`.

```shell
$ repacolor colorwheel rgb
[RGB color wheel]
$ repacolor scale red white black red | repacolor colorwheel
[red - white - black color wheel]
```

### `adjust-contrast`

Adjust the colors to match required contrast ratio.

If only one color is provided, chooses black or white based on the colors luminance.

If two colors are provided, tries to lighten/darken them to fulfill the contrast requirement. Starts to adjust the first color, then if it's not enough continues with the other.

Default contrast is 4.5 (WCAG AA). [More info on MDN.](https://developer.mozilla.org/en-US/docs/Web/Accessibility/Understanding_WCAG/Perceivable/Color_contrast)

```shell
$ repacolor adjust-contrast red --format=lhex
#ff0000
#000000  # chooses black for red
$ repacolor adjust-contrast "#555" "#5e8d87" --format=lhex
#1d1d1d  # #555 adjusted to be darker
#5e8d87
$ repacolor adjust-contrast "#5e8d87" "#555" --format=lhex
#b6cfcc  # #5e8d87 lightened
#555555
$ repacolor adjust-contrast "#5e8d87" "#555" -v
Colors adjusted. (2.0007 => 4.5224)
  #5e8d87   =>   #b6cfcc
  #555555   =>   #555555
```
