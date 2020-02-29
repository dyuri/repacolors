import click
import repacolors
import repacolors.palette
import repacolors.schemes
import sys


def from_stdin():
    colordef = []
    # read from stdin
    for line in sys.stdin:
        colordef.append(line.strip())

    return colordef


@click.group(invoke_without_command=False)
@click.pass_context
def color(ctx):
    pass


@color.command()
@click.argument("name", nargs=-1)
@click.option("--format", default="hexdisplay", help="Color format to show.")
def palette(name, format):
    """Get colors of given palette"""
    if len(name) == 0:
        names = repacolors.palette.PALETTES.keys()
        click.echo("List of available palette names:")
        click.echo(", ".join(names))
    else:
        colors = []
        for n in name:
            try:
                colors += repacolors.palette.get_palette(n)
            except KeyError:
                click.echo(f"Palette '{n}' not found.", err=True)

        for cdef in colors:
            c = repacolors.Color(cdef)
            c.print(format)


@color.command()
@click.argument("colordef", nargs=-1)
@click.option("--format", default="display", help="Color format to show.")
def display(colordef, format):
    """Display information about the provided colors."""
    if len(colordef) == 0:
        colordef = from_stdin()

    for cdef in colordef:
        c = repacolors.Color(cdef)
        c.print(format)


@color.command()
@click.argument("name", nargs=-1)
def colorwheel(name):
    """Display colorwheel defined by `name` or created by the colors provided via stdin."""
    if len(name) == 0:
        colors = from_stdin()
        cscale = repacolors.ColorScale(colors)
        cwheel = repacolors.ColorWheel(cscale)
    else:
        n = name[0].lower()
        if n in ["rgb", "hsl"]:
            cwheel = repacolors.schemes.RGB
        elif n in ["lab", "lch"]:
            cwheel = repacolors.schemes.LAB
        else:
            cwheel = repacolors.schemes.RYB

    cwheel.print()


@color.command()
@click.option("--format", default="display", help="Color format to show.")
@click.option("-n", "--number", "number", default=1, help="Number of colors to pick.")
def pick(format, number):
    """Pick colors from your desktop."""
    while number:
        number -= 1
        c = repacolors.Color.pick()
        c.print(format)


@color.command()
@click.argument("colors", nargs=-1)
@click.option("--format", default="display", help="Scale format to show.")
@click.option("-s", "--steps", "steps", default=None, type=int, help="Number of steps.")
def scale(colors, format, steps):
    """Display color scale defined by the colors provided."""
    if len(colors) == 0:
        colors = from_stdin()
    cscale = repacolors.scale.ColorScale(colors)
    cscale.print(fmt=format, steps=steps)


if __name__ == "__main__":
    color()
