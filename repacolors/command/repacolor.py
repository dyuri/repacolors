import click
import repacolors


@click.group(invoke_without_command=False)
@click.pass_context
def color(ctx):
    pass


@color.command()
@click.argument("colordef")
@click.option("--format", default="display", help="Color format to show.")
def display(colordef, format):
    c = repacolors.Color(colordef)
    c.print(format)


@color.command()
@click.option("--format", default="display", help="Color format to show.")
def pick(format):
    c = repacolors.Color.pick()
    c.print(format)


if __name__ == "__main__":
    color()
