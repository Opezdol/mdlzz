from build123d import (
    Circle,
    offset,
    Sketch,
    Align,
    Axis,
    Polygon,
    Pos,
    RegularPolygon,
    extrude,
    Part,
    Rectangle,
    Plane,
    fillet,
    Rot,
    loft,
)

from touch import Bl_Touch
from dataclasses import dataclass
from heater import DragonUHF
from base_vslot2020 import Vslot_Plate, Vslot_Roller  # , ass
from prop import Vent_Axial, Vent_Blower


@dataclass
class HGX_Lite:
    length = 51
    width = 25
    base_height = 7
    r_center = 4 / 2
    fix_r = 3 / 2
    fix_offset = 7.25
    fix_inter = 43.5

    @property
    def body(self) -> Part:
        res = extrude(
            Rectangle(height=self.width, width=self.length)
            - Pos(Y=self.width / 2 - self.fix_offset)
            * (
                Circle(self.r_center)
                + Pos(X=self.fix_inter / 2) * Circle(self.fix_r)
                + Pos(X=-self.fix_inter / 2) * Circle(self.fix_r)
            ),
            amount=self.base_height,
        )
        # basck plate for engine fix
        topf = Plane.XY.offset(self.base_height)
        plate = extrude(
            topf
            * Pos(Y=-self.width / 2)
            * Rectangle(width=41.5, height=5, align=(Align.CENTER, Align.MIN)),
            amount=38.5,
        )
        plate = fillet(plate.edges().filter_by(Axis.Y).group_by()[-1], 15)
        eng_plate = Plane.XZ.offset(self.width / 2)
        engine = extrude(
            eng_plate * Pos(Y=1.7 + 36.5 / 2) * Circle(36.5 / 2), amount=22.5
        )
        res += plate
        res += engine

        return Pos(Y=-self.width / 2 + self.fix_offset) * res


pusher = HGX_Lite()
bl_touch = Bl_Touch()
extruder = DragonUHF(simple=False)
axis_40 = Vent_Axial(side=40, fix=32, central_diam=38, height=11)
blow = Vent_Blower()

ass = Vslot_Plate()
ass_pos = Pos(Z=-33, Y=-20) * Rot(Z=180) * Rot(X=90)
extruder_pos = Pos(Z=-20) * Pos(Z=-extruder.radiator_height)
bl_touch_pos = Pos(Z=-20) * Pos(X=-30, Z=-extruder.height + bl_touch.nozzle_offset)
axis_40_pos = Pos(Y=15, Z=-30) * Rot(X=-90)
blow_pos = Pos(X=25, Z=-30, Y=blow.d / 2 - 10) * Rot(Z=90, Y=90)

# print(dir(ass.children[-1]))

show_object(pusher.body, name="HGX_Lite")
show_object(
    ass_pos * ass.body,
    name="base assembly",
)
show_object(
    extruder_pos * extruder.body,
    name="DragonUHF",
    options=dict(alpha=0.4, color="brown"),
)
show_object(
    bl_touch_pos * bl_touch.body,
    name="bl_touch",
    options=dict(color="blue"),
)
show_object(
    axis_40_pos * axis_40.minus_body(),
    name="Axis vent",
    options=dict(alpha=0.3, color="red"),
)
show_object(
    blow_pos * (blow.minus_body() + blow.duct()),
    name="Blow vent",
    options=dict(alpha=0.3, color="red"),
)

## Main body. DaFrame!
sk = Sketch() + [
    Plane.XY * ass.base_rect_sk,
    Plane.XY.offset(25) * offset(ass.base_rect_sk, amount=5),
    Plane.XY.offset(40) * offset(ass.base_rect_sk, amount=-8),
]
res = ass_pos * loft(sk)
show_object(res - blow_pos * (blow.minus_body() + blow.duct()), name="daFrame")
