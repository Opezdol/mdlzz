from build123d import Polyline, make_face, extrude, Plane, offset  # type: ignore

# from dataclasses import dataclass
from math import tau
import numpy as np

np.pi


class Epi:
    def __init__(self, ratio: int, d: float) -> None:
        """We build epicycloidal parametric gear
        N: int - Gear ratio
        """
        self.N = ratio + 1  # Num of coronal bearings
        self.r = d / 2
        self.R = self.from_minorD(d) / 2

    def from_majorD(self, D: float) -> float:
        """get diam of bearings from Major D"""
        return tau * D / (4 * self.N)

    def from_minorD(self, d: float) -> float:
        """Get MajorD defined by bearings"""
        return 4 * self.N * d / tau

    def excentricity(self) -> float:
        return self.r / 2

    def points(self, steps: int = 10):
        """Epytrohoidal points"""
        step = tau / steps
        t = np.arange(start=0, stop=tau - step, step=step)
        radsum = self.r + self.R
        xs = radsum * np.cos(t) - self.excentricity() * np.cos(radsum * t / self.r)
        ys = radsum * np.sin(t) - self.excentricity() * np.sin(radsum * t / self.r)
        res = [(x, y) for x, y in zip(xs, ys)]
        return res

    def build(self):
        line = Polyline(self.points(steps=500))
        # f = make_face(Plane.XY * line)
        return line


test = Epi(ratio=4, d=2.5)
test.points()
show_object(test.build(), name=" face")
