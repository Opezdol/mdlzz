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


class Rasp_hold:
    def __init__(self) -> None:
        self.base_w = 190 - 22
        self.base_h = 90
        self.r_h = 58
        self.r_w = 85.5
        self.point_r = 7 / 2
        self.upmove = 2.4
        self.outer_w = 106
        self.outer_h = 95.4
        self.outer_thick = 1.4
        self.outer_champher = 9
        self.outer_inc_h = 6
        self.outer_inc_w = 41
        self.up = 5
        self.base_thick = 3

    def base_pnts(self) -> GridLocations:
        return GridLocations(
            x_spacing=self.base_w, x_count=2, y_count=2, y_spacing=self.base_h
        )

    def pi_pnts(self) -> GridLocations:
        return GridLocations(
            x_spacing=self.r_w, x_count=2, y_count=2, y_spacing=self.r_h
        )

    def build(self):
        pnts = [pnt * Circle(3.8 / 2) for pnt in self.base_pnts()]
        print(pnts)

        # Pi fixes
        fix_central_hole = [
            pnt * extrude(Circle(2.7 / 2), amount=10, both=True)
            for pnt in self.pi_pnts()
        ]
        screw_minus = [
            pnt * extrude(Circle(4.5 / 2), amount=self.up - 2, both=True)
            for pnt in self.pi_pnts()
        ]

        res = make_hull([pnt.edges() for pnt in pnts])
        res = offset(res, amount=5)
        res -= pnts
        res = extrude(res, amount=-self.base_thick)
        # __________
        fix = Pos(Z=self.up) * extrude(Circle(self.point_r), amount=-self.up, taper=-15)
        fixes = [pnt * fix for pnt in self.pi_pnts()]
        ## outerbox
        skout = Pos(Y=-self.r_h / 2 - 10) * Rectangle(
            width=self.outer_w, height=self.outer_h, align=(Align.CENTER, Align.MIN)
        )
        skout = chamfer(skout.vertices(), length=self.outer_champher)
        skres = skout - offset(skout, -self.outer_thick)
        # show_object(skres, name="debug")
        # Sdcard incision
        sd = Plane.XZ * RectangleRounded(
            width=20, height=6, radius=1, align=(Align.CENTER, Align.CENTER)
        )
        sd = Pos(X=-20, Y=-self.r_w / 2, Z=self.up) * sd
        sd = extrude(sd, amount=10, both=True)
        # show_object(sd, name="minus sd")

        res += extrude(skout, amount=-self.base_thick)
        res += extrude(skres, amount=self.up + self.upmove)
        res += fixes
        res -= fix_central_hole
        res -= screw_minus
        res -= sd
        return res


t = Rasp_hold()
show_object(t.build(), name="base")
