from build123d import (
    Helix,
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


class Adapter_R_to_r:
    def __init__(self, D: float = 125.7, d: float = 99) -> None:
        self.R = D / 2
        self.r = d / 2
        self.tiny = 0.15
        self.thick = 8
        self.height = 40

    def build(self):
        sk1 = Circle(self.R + self.tiny)
        sk0 = Circle(self.r + self.tiny)
        pl = Plane.XY
        perloft = Sketch() + [
            sk0,
            pl.offset(15) * sk0,
            pl.offset(self.height - 15) * sk1,
            Plane.XY.offset(self.height) * sk1,
        ]
        res = loft(perloft, ruled=True)

        sk0 = offset(sk0, amount=self.thick)
        sk1 = offset(sk1, amount=self.thick)
        perloft = Sketch() + [
            sk0,
            pl.offset(15) * sk0,
            pl.offset(self.height - 15) * sk1,
            Plane.XY.offset(self.height) * sk1,
        ]
        out = loft(perloft)
        return out - res

    def make_helix(self, r: float):
        tpur = 1.82 / 2
        sk = Helix(pitch=tpur * 2 + 0.25, radius=r, height=2.3)
        res = sweep(
            Plane.XZ * Pos(X=r + tpur) * Circle(tpur),
            path=sk,
        )
        return res


t = Adapter_R_to_r()
base = t.build()
base -= Pos(Z=t.height - 4) * t.make_helix(r=t.R)
base -= Pos(Z=2) * t.make_helix(r=t.r)
show_object(base, name="base")
show_object(Pos(Z=2) * t.make_helix(r=t.r), name="make_helix")
show_object(Pos(Z=t.height - 4) * t.make_helix(r=t.R), name="helo1")
