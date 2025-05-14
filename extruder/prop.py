from dataclasses import field, dataclass
from build123d import (
    Sketch,
    loft,
    Plane,
    GridLocations,
    Rectangle,
    Circle,
    SlotArc,
    Rot,
    SlotOverall,
    extrude,
    GeomType,
    fillet,
    Pos,
    offset,
    Align,
    Axis,
)
from build123d.topology import Compound


@dataclass
class Vent_Axial:
    side: float = field(repr=True, default=140.5)
    height: float = field(repr=True, default=25)
    fix: float = field(repr=True, default=125)
    central_diam: float = field(repr=True, default=134)
    fillet: float = field(repr=True, default=2)

    @property
    def obj(self):
        return extrude(self.sk, self.height)

    @property
    def sk(self) -> Sketch:
        sketch = Plane.XY * (self.cut - Circle(self.central_diam / 2))
        sketch -= [loc * Circle(2) for loc in self.fixes]  # type:ignore
        return sketch

    @property
    def fixes(self) -> GridLocations:
        return GridLocations(self.fix, self.fix, 2, 2)

    @property
    def cut(self):
        "Outer profile of Prop"
        sketch = Rectangle(self.side, self.side)
        sketch = fillet(sketch.vertices(), self.fillet)
        return sketch

    @property
    def central(self):
        return Circle(self.central_diam / 2)

    def minus_body(self, f: float = 0.2):
        return extrude(offset(self.cut, amount=f), amount=self.height)


axis_40 = Vent_Axial(side=40, fix=32, central_diam=38, height=11)
# show_object(axis_40.obj, name="40mm axis fan")
# show_object(axis_40.central, name="vent ")


@dataclass
class Vent_Blower:
    d = 48.5
    h = 51.5
    fix_outer = 64.5
    fix_thick = 7
    fix = 58
    thick = 15.5
    out_w = 17
    out_h = 13
    fillet_r = 2

    @property
    def sk(self) -> Sketch:
        sk = Plane.XY * Circle(self.d / 2)
        fix = SlotOverall(width=self.fix_outer, height=self.fix_thick, rotation=-45)
        rect = Pos(X=-self.d / 2) * Rectangle(
            width=20, height=self.d / 2 + 3, align=(Align.MIN, Align.MAX)
        )
        # select vertices for fillet

        res = sk + rect

        v1 = res.vertices()
        inter = v1 - rect.vertices()
        res = fillet(inter.sort_by(Axis.Y)[0], radius=self.fillet_r)
        res += fix
        res = fillet(res.vertices() - v1 - fix.vertices(), radius=self.fillet_r)
        return res

    def fixes(self):
        return Rot(Z=-45) * GridLocations(
            x_spacing=self.fix, x_count=2, y_count=1, y_spacing=0
        )

    def minus_body(self, f: float = 0.2) -> Compound:
        resk = offset(self.sk, amount=f)
        return extrude(resk, amount=self.thick)

    def vent(self, f: float = 0):
        # return offset(self.minus_body(f=0).faces().sort_by(Axis.Y)[0], amount=f)
        return self.minus_body(f=0).faces().sort_by(Axis.Y)[0]

    def duct(self):
        sk = Sketch() + [
            offset(self.vent(), amount=2),
            Pos(Y=-3.5, Z=-5) * self.vent(),
            Pos(Y=-10, Z=-20) * Rot(X=10) * (Plane(self.vent()) * Circle(8)),
            Pos(Y=-15, Z=-35) * (Plane(self.vent()) * Circle(8)),
        ]
        res = loft(sk)
        # show_object(res)
        return res


# blow = Vent_Blower()
# blow.duct()
# show_object(blow.sk, name="sketck")
# show_object(blow.minus_body(f=0.3), name="minus")
# show_object(blow.vent(), name="vent")
# print(blow.vent().area)
# show_object([Circle(1).locate(loc) for loc in blow.fixes()], name="plus")
#
