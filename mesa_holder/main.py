from OCP import Geom
from build123d import (
    Align,
    GeomType,
    Select,
    chamfer,
    make_hull,
    SlotOverall,
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

from numpy.__config__ import show

INCH = 25.4


@dataclass
class Din_Fix:
    width = 25
    height = 52
    thick = 4
    clap_inner_h = 42
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
        res += self.core_fix()

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
        res -= self.core_fix_slot()
        # show_object(res, name="body", options={"alpha": 0.5, "color": (64, 164, 223)})
        # show_object(t.movt(), name="movt", options=rand_color(alpha=0.6))  # type:ignore
        return res

    def core_fix(self, offs=0.0):
        fix_off = 1.5 + offs
        fix_w = self.width - 15 + offs
        sk_minus = Rectangle(self.clap_w, self.clap_inner_h)
        faces = Sketch() + [
            RectangleRounded(width=fix_w, height=self.height, radius=2),
            Pos(0, 0, self.thick / 2)
            * RectangleRounded(width=fix_w, height=self.height + fix_off * 2, radius=2),
        ]
        res = loft(faces, ruled=True)
        return res - extrude(sk_minus, amount=self.thick / 2)

    def core_fix_minus(self):
        offs = 0.15
        sk = RectangleRounded(
            width=self.width + offs * 2, height=self.height + offs * 2, radius=2
        )
        res = extrude(sk, amount=self.thick + offs)  # type:ignore
        res += self.core_fix(offs=offs)
        return Pos(0, 0, -self.thick) * res

    def core_fix_slot(self):
        sk = SlotOverall(width=self.width - 5, height=1.8)
        res = Pos(
            0, -self.height / 2 + (self.height - self.clap_inner_h) / 4, 0
        ) * extrude(sk, amount=self.thick, taper=5)
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
        length = 14
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


@dataclass
class Test_plate:
    def build(self, fix: Din_Fix):
        sk = RectangleRounded(width=1.5 * fix.width, height=1.2 * fix.height, radius=2)
        res = extrude(sk, amount=fix.thick * 1.1)
        topf = Plane(res.faces().sort_by(Axis.Z)[-1])
        res -= topf * fix.core_fix_minus()
        return res


@dataclass
class Mesa_Din_Holder:
    conn_w = 3.7 * INCH
    conn_r1 = (1.9 - 0.15) * INCH
    conn_r2 = (3.650 - 0.15) * INCH
    conn_r3 = (5.45 - 0.15) * INCH
    conn_r4 = (6.35 - 0.15) * INCH

    def fixes(self) -> list[Location]:
        res = [
            Location((0, -self.conn_w / 2, 0)),
            Location((0, self.conn_w / 2, 0)),
            Location((self.conn_r1, -self.conn_w / 2, 0)),
            Location((self.conn_r1, self.conn_w / 2, 0)),
            Location((self.conn_r2, -self.conn_w / 2, 0)),
            Location((self.conn_r2, self.conn_w / 2, 0)),
            Location((self.conn_r3, -self.conn_w / 2, 0)),
            Location((self.conn_r3, self.conn_w / 2, 0)),
            Location((self.conn_r4, -self.conn_w / 2, 0)),
            Location((self.conn_r4, self.conn_w / 2, 0)),
        ]
        return res

    def build(self, locs: list[Location], fix: Din_Fix):
        sl = Sketch() + [loc * Circle(0.5) for loc in locs]
        res = offset(make_hull(sl.edges()), amount=5)
        show_object(extrude(res, amount=5), name="sl")

    def internal_build(self, fix: Din_Fix):
        sl = Sketch() + [loc * Circle(1) for loc in self.fixes()]
        sk = Sketch() + [loc * Circle(3.5) for loc in self.fixes()]
        res = make_hull(sl.edges())
        res = offset(res, amount=10)
        # res -= sl
        body = extrude(res, amount=5)
        body = chamfer(body.edges().group_by(Axis.Z)[0], length=1)
        body = chamfer(body.edges().group_by(Axis.Z)[-1], length=1)
        pins = extrude(sk, amount=7)
        comb = pins + body
        res = fillet(
            new_edges(body, combined=comb)
            .group_by(Axis.Z)[0]
            .filter_by(GeomType.CIRCLE),
            radius=1,
        )

        botf = Plane(res.faces().sort_by(Axis.Z)[0])
        res -= botf * Pos(-self.conn_r4 / 3, 0, 0) * fix.core_fix_minus()
        res -= botf * Pos(self.conn_r4 / 3, 0, 0) * fix.core_fix_minus()

        topf = Plane(res.faces().sort_by(Axis.Z)[-1])
        sk = Sketch() + [loc * Circle(4.8 / 2) for loc in self.fixes()]
        res -= extrude(Pos(0, 0, 7) * sk, amount=-3.2)
        return res


t = Din_Fix()
test = Test_plate()
msa = Mesa_Din_Holder()
show_object(msa.internal_build(fix=t), name="hull")
show_object(test.build(fix=t))
show_object(
    t.build(), name="Din_Fix", options=rand_color(alpha=0.3)
)  # type:ignore   )  # type:ignore
