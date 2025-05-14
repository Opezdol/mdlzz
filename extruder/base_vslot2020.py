from dataclasses import dataclass
import copy

from build123d import (
    Align,
    Axis,
    Circle,
    GridLocations,
    Compound,
    Hole,
    Keep,
    Location,
    Part,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    RectangleRounded,
    RegularPolygon,
    Rot,
    Sketch,
    SlotCenterPoint,
    SlotCenterToCenter,
    SlotOverall,
    Trapezoid,
    Wire,
    chamfer,
    extrude,
    fillet,
    make_face,
    mirror,
    revolve,
    split,
)


@dataclass
class Vslot_Roller:
    main_d = 23.89
    roller_d = 16
    width = 10.23
    width_inn = 5.89
    center_d = 5

    def body(self):
        sk = Rectangle(self.width, self.main_d)
        sk = chamfer(sk.vertices(), length=(self.width - self.width_inn) / 2, angle=45)
        sk = split(sk, bisect_by=Plane.XZ)  # type: ignore
        res = revolve(sk, axis=Axis.X)  # type: ignore
        # return Pos(Z=self.width / 2 + 7) * Rot(Y=90) * res
        return res


@dataclass
class Vslot_profile:
    dim = 20
    inc_open_inner = 6.25
    inc_open_outer = 9.16
    inc_w = 11
    inc_h = 4.3
    inc_open_thick = 1.8
    cntr_hoe = 4.2 / 2

    def trapex(self):
        pnts = [
            (0, 0),
            (self.inc_open_inner / 2, 0),
            (self.inc_w / 2, (self.inc_w - self.inc_open_inner) / 2),
            (self.inc_w / 2, self.inc_h),
            (self.inc_open_inner / 2, self.inc_h),
            (self.inc_open_inner / 2, self.inc_h + 0.2),
            (self.inc_open_outer / 2, self.inc_h + self.inc_open_thick),
            (0, self.inc_h + self.inc_open_thick),
        ]
        ln = Polyline(pnts)
        ln += mirror(ln, Plane.YZ)
        res = make_face(Plane.XY * ln)  # type: ignore
        # res = fillet(res.vertices(), radius=0.04)
        return res

    def quarter(self):
        # res = Trapezoid(width=11, height=4.30, left_side_angle=45)
        # inner_w = 20 - (4.3 + 1.8) * 2
        res = RectangleRounded(20, 20, radius=1)
        inc = Pos(Y=10 - 4.3 - 1.8) * self.trapex()
        inc += mirror(inc, Plane.XZ)  # type: ignore
        inc += Rot(Z=90) * inc  # type: ignore
        res -= inc
        # center hoe
        res -= Circle(2.1)
        return res


@dataclass
class Vslot_Plate:
    base_thick = 3
    base_w = 65.5
    r2_offset = 12.75
    r5_offset = 52.75

    @property
    def three_in_row(self) -> list[Location]:
        return [
            loc
            for loc in GridLocations(x_count=3, y_count=1, x_spacing=19.85, y_spacing=0)
        ]

    def top_off(self, offset: float = 0) -> Pos:
        return Pos(Y=(self.base_w / 2 - offset))

    @property
    def base_rect_sk(self):
        return RectangleRounded(
            self.base_w,
            self.base_w,
            radius=3,
            align=(Align.CENTER, Align.CENTER),
        )

    def row1(self, base=False):
        """
        if 'base' == True, it will return base_sk row1 is constructed of
        """
        base_sk = SlotCenterToCenter(center_separation=6.5, height=3)
        res = Sketch() + [loc * base_sk for loc in self.three_in_row]
        return base_sk if base else res

    @property
    def wheel_row(self) -> list[Location]:
        return GridLocations(x_count=2, y_count=1, x_spacing=37.9, y_spacing=0)

    @property
    def wheelz(self) -> list[Location]:
        res = []
        res.extend([-self.top_off(self.r2_offset) * loc for loc in self.wheel_row])
        res.extend([-self.top_off(self.r5_offset) * loc for loc in self.wheel_row])
        return res

    def row2(self) -> Sketch:
        res = Sketch() + [
            loc * Circle(7.2 / 2)
            # for loc in GridLocations(x_count=2, y_count=1, x_spacing=37.9, y_spacing=0)
            for loc in self.wheel_row
        ]
        res += SlotCenterPoint(center=(0, 0), point=(10, 0), height=5)
        return res  # type: ignore

    def row3(self) -> Sketch:

        res = Sketch() + [loc * Circle(5.1 / 2) for loc in self.three_in_row]
        return res  # type: ignore

    def rowCenter(self) -> Sketch:
        res = Sketch() + [
            loc * Circle(5.1 / 2)
            for loc in GridLocations(x_count=5, x_spacing=9.85, y_spacing=0, y_count=1)
        ]
        res += Pos(X=-9.85 * 2) * Circle(7.2 / 2)
        return res.clean()  # type: ignore

    @property
    def body(self):
        ## Top row hoes
        res = self.base_rect_sk - self.top_off(5.05) * self.row1()
        ## second row
        res -= self.top_off(self.r2_offset) * self.row2()
        ## row3
        res -= self.top_off(22.75) * self.row3()
        ## Center row
        res -= self.rowCenter()
        ##  other rows are symmetrical
        res -= self.top_off(42.75) * self.row3()
        res -= self.top_off(self.r5_offset) * self.row2()
        res -= self.top_off(60.45) * self.row1()

        return extrude(res, amount=self.base_thick)


# Assembly
plate = Vslot_Plate()
profile = Vslot_profile().quarter()
roller = Vslot_Roller().body()
# label da shit
plate_body = plate.body
plate_body.label = "plate"
roller.label = "roller"
profile_body = Pos(Z=-12) * Rot(Y=90) * extrude(profile, amount=40, both=True)
profile_body.label = "profile"
whlz = [loc * Pos(Z=12) * Rot(Y=90) * copy.copy(roller) for loc in plate.wheelz]
ass = Compound(label="assembly", children=whlz)
profile_body.parent = ass
plate_body.parent = ass
print(ass.show_topology())
# show_object(ass, name="assembly")
