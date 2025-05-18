from build123d import (
    Align,
    loft,
    offset,
    GridLocations,
    Pos,
    Circle,
    Keep,
    Polygon,
    RegularPolygon,
    Sketch,
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
    width = 25
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

        # lip top
        lip_th = (self.height - self.clap_inner_h) / 2
        lip_pos = Pos(0, self.height / 2, self.thick)
        lip_sk = lip_pos * RectangleRounded(
            width=self.width,
            height=lip_th,
            radius=2,
            align=(Align.CENTER, Align.MAX),
        )
        lip_enforce = Sketch() + [
            pos * Circle(0.5)
            for pos in GridLocations(
                x_count=4, x_spacing=self.clap_w / 5, y_count=1, y_spacing=0
            )
        ]
        lip_enforce = extrude(lip_enforce, amount=(self.thick + 1.5) / 2, both=True)
        lip_enforce = lip_pos * Pos(0, -lip_th / 2, -1) * lip_enforce
        lip_faces = [lip_sk, Pos(0, 0, 0.7) * lip_sk, Pos(0, 0, 2) * offset(lip_sk, 1)]
        lip = loft(lip_faces, ruled=True)
        # _____________________-

        # build yourself
        minus = Pos(0, 2, 0) * self.incisio(r_add=1, length=self.clap_inner_h / 2 + 2)
        minus += mirror(minus, about=Plane.YZ)
        res -= minus
        res += self.sling3()
        res += self.movt()
        res += lip
        res -= lip_enforce
        # show_object(res, name="body", options={"alpha": 0.5, "color": (64, 164, 223)})
        # show_object(t.movt(), name="movt", options=rand_color(alpha=0.6))  # type:ignore
        return res

    def sling3(self):

        ## Geometry 5-th grade. 90 minutes to solve it.... Shame on you!!
        sling_step = 3
        lateral_offset = 2.5
        sling_th = 2.9
        arc_d = 180
        x = self.clap_w / 2 - lateral_offset
        y = 1.5
        h = sqrt(x * x + y * y)
        up_move = h * sling_step / x
        swings = 3
        ## Calc ended....

        l0 = Line((0, 0), (x, y))
        l1 = JernArc(
            start=l0 @ 1, tangent=l0 % 1, radius=sling_step / 2, arc_size=arc_d
        )
        l2 = Line(l1 @ 1, (0, up_move))
        sk = Plane.YZ * RectangleRounded(
            width=sling_th,
            height=self.thick,
            align=(Align.CENTER, Align.MIN),
            radius=0.5,
        )
        l_tot = l0 + l1 + l2  # type:ignore
        base = l_tot + mirror(
            l_tot.moved(Location((0, up_move, 0))), about=Plane.YZ  # type:ignore
        )
        for i in range(1, swings):
            base += base.moved(Location((0, up_move * 2 * i, 0)))  # type:ignore
        base += Line(base @ 1, (0, self.height))
        # show_object(base, name = 'baseline')

        v = base.vertices().filter_by(lambda v: -0.005 <= v.X <= 0.005)  # type:ignore
        linea = fillet(v, radius=2)
        linea = linea.intersect(Rectangle(self.height - self.tiny, self.height - 2))
        # show_object(linea, name="linea")
        res = sweep(sk, path=linea)  # type:ignore
        return res

    def movt(self):
        sk = Circle(radius=2.6 / 2)
        length = 15
        rad = 1
        up = 1
        lateral = self.incisio(inc=1.7, length=length - rad * 2)
        lateral += mirror(lateral, about=Plane.YZ)
        ## Base plate
        sk += Pos(0, up, 0) * RectangleRounded(
            width=self.clap_w - self.tiny,
            height=length,
            radius=rad,
            align=(Align.CENTER, Align.MAX),
        )
        res = extrude(sk, amount=self.thick)
        # lip
        lip_th = 5
        lip_pos = Pos(0, -(length - up), self.thick)
        lip_sk = lip_pos * RectangleRounded(
            width=self.clap_w - self.tiny,
            height=lip_th,
            radius=rad,
            align=(Align.CENTER, Align.MIN),
        )
        lip_enforce = Sketch() + [
            pos * Circle(0.5)
            for pos in GridLocations(
                x_count=4, x_spacing=self.clap_w / 5, y_count=1, y_spacing=0
            )
        ]
        lip_enforce = extrude(lip_enforce, amount=(self.thick + 1.5) / 2, both=True)
        lip_enforce = lip_pos * Pos(0, lip_th / 2, -1) * lip_enforce

        lip_faces = [lip_sk, Pos(0, 0, 0.7) * lip_sk, Pos(0, 0, 2) * offset(lip_sk, 1)]
        lip = loft(lip_faces, ruled=True)
        return res + lateral + lip - lip_enforce

    def incisio(self, inc=2.0, length=20.0, r_add=0.0):
        sk = (
            Plane.XZ
            * Pos(self.clap_w / 2 + self.clap_offset + inc, self.thick / 2)
            * RegularPolygon(
                radius=self.thick / 2 + r_add,
                side_count=3,
                rotation=0,
                align=(Align.MAX, Align.CENTER),
            )
        )
        sk = fillet(sk.vertices().sort_by(Axis.X)[-1], radius=0.5)
        return extrude(sk, amount=length)


t = Din_Fix()
show_object(
    t.build(), name="Din_Fix", options=rand_color(alpha=0.3)
)  # type:ignore   )  # type:ignore
