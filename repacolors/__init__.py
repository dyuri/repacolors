"""
`repacolors` provides classes, functions and a command line utility to convert
colors from one color space / format to other, create `mathplotlib` compatible
color scales and more.

.. include:: ./documentation.md
"""

from .colors import Color
from .scale import ColorScale
from .cubehelix import CubeHelix

__version__ = "0.4.0"
