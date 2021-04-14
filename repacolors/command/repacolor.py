import click
import repacolors
import repacolors.palette
import repacolors.schemes
import sys
import os
import subprocess  # nosec


def from_stdin():
    colordef = []
    # read from stdin
    for line in sys.stdin:
        colordef.append(line.strip())

    return colordef


def pick_external(picker="xcolor"):
    proc = subprocess.Popen(picker, stdout=subprocess.PIPE)  # nosec
    res = proc.communicate()[0].strip().decode()
    return repacolors.Color(res)


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
@click.argument("colordef", nargs=-1)
@click.option("--contrast", default=4.5, help="Required contrast")
@click.option("--format", default="display", help="Color format to show.")
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True, help="Print verbose output.")
def adjust_contrast(colordef, contrast, format, verbose):
    """Adjust the colors to match required contrast ratio."""
    # check stdin for more colors
    if len(colordef) < 2 and not sys.stdin.isatty():
        stdincolors = from_stdin()
        colordef = (list(colordef) + list(stdincolors))[:2]

    if len(colordef) == 0:
        click.echo("At least one color definition required!")
        sys.exit(1)

    c1 = repacolors.Color(colordef[0])
    # still not enough colors, fall back to black/white
    if len(colordef) < 2:
        # using #757575 as middle point
        c2 = repacolors.Color("#fff") if c1.luminance < .178 else repacolors.Color("#000")
    else:
        c2 = repacolors.Color(colordef[1])

    adjc1, adjc2 = c1.adjust_contrast(c2, contrast)

    if not verbose or not sys.stdout.isatty():
        adjc1.print(format)
        adjc2.print(format)

    else:
        if c1 == adjc1 and c2 == adjc2:
            print(f"Contrast was already OK! ({c1.contrast_ratio(c2)} > {contrast})")
            print(f"{adjc2.termfg}{adjc1.termbg}  {adjc1.lhex}  ")
            print(f"{adjc1.termfg}{adjc2.termbg}  {adjc2.lhex}  ")
        else:
            print(f"Colors adjusted. ({c1.contrast_ratio(c2):.4f} => {adjc1.contrast_ratio(adjc2):.4f})")
            print(f"{c2.termfg}{c1.termbg}  {c2.lhex}  {c2.termreset} => {adjc2.termfg}{adjc1.termbg}  {adjc1.lhex}  ")
            print(f"{c1.termfg}{c2.termbg}  {c1.lhex}  {c1.termreset} => {adjc1.termfg}{adjc2.termbg}  {adjc2.lhex}  ")

        print(c1.termreset)
        adjc1.print(format)
        adjc2.print(format)


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
@click.option("-c", "--copy", "copy", default=False, is_flag=True, help="Copy to clipboard (using `xsel`)")
def pick(format, number, copy):
    """Pick colors from your desktop."""
    # TODO copy to clipboard
    # TODO draw color wheel

    colorpicker = os.environ.get("COLORPICKER")
    colors = []

    # if color picker is not set, try to use integrated one
    if not colorpicker:
        try:
            import repacolors.picker
            colors = repacolors.picker.pick(number)
        except ImportError:
            pass

    while number > len(colors):
        colors.append(pick_external())

    for c in colors:
        c.print(format)

    if copy:
        try:
            proc = subprocess.Popen(["xsel", "-p"], stdin=subprocess.PIPE)  # nosec
            proc.stdin.write(c.lhex.encode())
            proc.stdin.close()
            proc.wait()
        except subprocess.SubProcessError:
            pass


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
