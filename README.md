# repacolors

Small library for color conversion, manipulation, etc.

[![Build Status](https://travis-ci.com/dyuri/repacolors.svg?branch=master)](https://travis-ci.com/dyuri/repacolors)

## Install

```
$ pip install repacolors
```

## `repacolor` command

```
$ repacolor --help                                                                         
Usage: repacolor [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  colorwheel  Display colorwheel defined by `name` or created by the colors...
  display     Display information about the provided colors.
  palette     Get colors of given palette
  pick        Pick colors from your desktop.
  scale       Display color scale defined by the colors provided via stdin.
```

### `display`

Display color information in the terminal.

```
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

Executes color picker (`xcolor`) and displays the picked color.

```
$ repacolor pick
```

### `palette`

Display the colors of the palette. If no palette name provided, it shows the palettes available.

```
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

```
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

```
$ repacolor colorwheel rgb
[RGB color wheel]
$ repacolor palette red white black red | repacolor colorwheel
[red - white - black color wheel]
```
