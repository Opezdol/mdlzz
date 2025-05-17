from build123d import (
    Align,
    Pos,
    Circle,
    Keep,
    Polygon,
    RegularPolygon,
    Vertex,
    JernArc,
    Axis,
    Vector,
    Line,
    Location,
    Plane,
    PolarLine,
    Rectangle,
    RectangleRounded,
    Spline,
    extrude,
    fillet,
    mirror,
    new_edges,
    split,
    sweep,
)
from dataclasses import dataclass
from math import sqrt

INCH = 2.54


@dataclass
class Mesa_Din_Holder:
    conn_w = 3.7 * INCH
    conn_r1 = (1.9 - 0.15) * INCH
    conn_r2 = (3.650 - 0.15) * INCH
    conn_r3 = (5.45 - 0.15) * INCH
    conn_r4 = (6.35 - 0.15) * INCH


@dataclass
class Din_Fix:
    width = 33
    height = 52
    thick = 4
    clap_inner_h = 43
    clap_w = 15.5
    clap_offset = 0.5
    clap_h = 3
    clap_pre_tight = -2.5
    din_w = 35
    din_h = 7.5
    din_th = 1
    din_inn = 25
    tiny = 0.15

    def build(self):
        sk = RectangleRounded(width=self.width, height=self.height, radius=2)
        sk -= RectangleRounded(
            width=self.clap_w + self.clap_offset * 2, height=self.clap_inner_h, radius=2
        )
        res = extrude(sk, amount=self.thick)  # type:ignore
        show_object(res, name="body", options={"alpha": 0.5, "color": (64, 164, 223)})

        show_object(
            t.sling3(), name="sling3", options=rand_color(alpha=0.7)  # type:ignore
        )  # type:ignore
        show_object(t.movt(), name="movt", options=rand_color(alpha=0.6))  # type:ignore
        return extrude(sk, amount=self.thick)  # type:ignore

    def sling3(self):

        ## Geometry 5-th grade. 90 minutes to solve it.... Shame on you!!
        sling_step = 2.6
        lateral_offset = 2
        arc_d = 180
        x = self.clap_w / 2 - lateral_offset
        y = 1.8
        h = sqrt(x * x + y * y)
        up_move = h * sling_step / x
        swings = 4
        ## Calc ended....

        l0 = Line((0, 0), (x, y))
        l1 = JernArc(
            start=l0 @ 1, tangent=l0 % 1, radius=sling_step / 2, arc_size=arc_d
        )
        l2 = Line(l1 @ 1, (0, up_move))
        sk = Plane.YZ * RectangleRounded(
            width=lateral_offset,
            height=self.thick,
            align=(Align.CENTER, Align.MIN),
            radius=0.5,
        )
        l_tot = l0 + l1 + l2  # type:ignore
        base = l_tot + mirror(
            l_tot.moved(Location((0, up_move, 0))), about=Plane.YZ  # type:ignore
        )
        for i in range(1, 3):
            base += base.moved(Location((0, up_move * 2 * i, 0)))  # type:ignore
        base += Line(base @ 1, (0, self.height))
        # show_object(base, name = 'baseline')

        v = base.vertices().filter_by(lambda v: -0.005 <= v.X <= 0.005)  # type:ignore
        linea = fillet(v, radius=3)
        linea = linea.intersect(Rectangle(self.height - self.tiny, self.height - 2))
        res = sweep(sk, path=linea)  # type:ignore
        return res

    def movt(self):
        sk = Circle(radius=2.6 / 2)
        length = 15
        rad = 1
        lateral = self.incisio(length=length - rad * 2)
        lateral += mirror(lateral, about=Plane.YZ)
        ## Base plate
        sk += Pos(0, 1, 0) * RectangleRounded(
            width=self.clap_w - self.tiny,
            height=length,
            radius=rad,
            align=(Align.CENTER, Align.MAX),
        )
        res = extrude(sk, amount=self.thick)
        # lip
        return res + lateral

    def incisio(self, inc=2.0, length=20.0):
        sk = (
            Plane.XZ
            * Pos(self.clap_w / 2 + self.clap_offset + inc, self.thick / 2)
            * RegularPolygon(
                radius=self.thick / 2,
                side_count=3,
                rotation=0,
                align=(Align.MAX, Align.CENTER),
            )
        )
        sk = fillet(sk.vertices().sort_by(Axis.X)[-1], radius=0.5)
        return extrude(sk, amount=length)


t = Din_Fix()
show_object(t.build(), name="sk")  # type:ignore
