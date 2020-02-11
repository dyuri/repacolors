## The `repacolor` command

### Display information about a color

```
$ repacolor display red

 ##########  red - #ff0000
 ##########  rgb(255, 0, 0)
 ##########  hsl(0, 100%, 50%)
 ##########  lab(53.24%, 80.09 67.2)
 ##########
 ##########
```

It supports multiple formats:

- color name (`red`)
- hexadecimal color notation (`#f00` or `#ff0000aa`)
- css color notation (`rgb()`, `hsl()`, `hwb()`, `lab()`, `gray()`)
- any string will generate some color

