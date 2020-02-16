from .colors import Color
from .types import RGBTuple
from .scale import ColorScale, project_domain, linear_ip_f
from typing import Union, List
import math


def _cubehelix(pos: float, start: float = 0, rotations: float = -1.5, lightness: float = None, hue: float = None):
    if lightness is None:
        lightness = pos

    if hue is None:
        hue = 1

    alpha = math.tau * ((start + .3333) + (rotations * pos))
    amp = (hue * lightness * (1 - lightness)) / 2
    cos_a = math.cos(alpha)
    sin_a = math.sin(alpha)
    r = lightness + amp * ((-0.14861 * cos_a) + (1.78277 * sin_a))
    g = lightness + amp * ((-0.29227 * cos_a) - (0.90649 * sin_a))
    b = lightness + amp * (1.97294 * cos_a)

    return Color(RGBTuple(r, g, b))


class CubeHelix(ColorScale):
    """CubeHelix color scale

    Dave Green's [cubehelix color scheme](http://www.mrao.cam.ac.uk/~dag/CUBEHELIX/)
    """

    def __init__(
        self,
        start: float = 0,
        rotations: float = -1.5,
        lightness: Union[float, List[float]] = [0, 1],
        hue: Union[float, List[float]] = [1, 1],
        gamma_correction: float = 1.0,
        domain: List[float] = None,
        gamma: float = 1.0,
        luminance_map: List[float] = [0, 100],
        name: str = "cubehelix"
    ):
        super().__init__(
            [Color("#000"), Color("#fff")],
            domain=domain,
            gamma=gamma,
            cspace="lab",
            gamma_correction=gamma_correction,
            interpolator="linear",
            luminance_map=luminance_map,
            name=name
        )

        self.start = start
        self.rotations = rotations

        self.hue = hue
        self.lightness = lightness

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, hue: Union[float, List[float]]):
        if isinstance(hue, (float, int)):
            hue = [hue, hue]
        self._hue = hue

    @property
    def lightness(self):
        return [lumin / 100 for lumin in self.luminance_map]

    @lightness.setter
    def lightness(self, lightness: Union[float, List[float]]):
        if isinstance(lightness, (float, int)):
            lightness = [lightness, lightness]
        self.luminance_map = [light * 100 for light in lightness]

    def _get_color_for_pos(self, pos: float) -> Color:
        projpos = project_domain(pos, self.domain)

        if self.gamma != 1.0:
            projpos = projpos ** self.gamma

        lightness = (linear_ip_f(self.luminance_map, projpos) / 100) ** self.gamma_correction
        hue = linear_ip_f(self.hue, projpos)

        return _cubehelix(
            projpos,
            start=self.start,
            rotations=self.rotations,
            lightness=lightness,
            hue=hue
        )
