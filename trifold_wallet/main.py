from build123d import (
    Kind,
    Side,
    offset,
    Align,
    Rot,
    Curve,
    Ellipse,
    make_face,
    revolve,
    Pos,
    Circle,
    Axis,
    Line,
    Plane,
    Rectangle,
    RectangleRounded,
    extrude,
    fillet,
    split,
)
from dataclasses import dataclass


@dataclass
class Wallet:
    ext_panel_width = 136.525 * 2
    ext_panel_height = 101.6
    ext_panel_r = 10

    def ext_panel(self):
        res = RectangleRounded(
            width=self.ext_panel_width,
            height=self.ext_panel_height,
            radius=self.ext_panel_r,
        )
        res = split(res, bisect_by=Plane.YZ)
        edgs = res.edges().sort_by(Axis.X)[1:].sort_by(Axis.Y)[:-2]
        sew_line = offset(
            edgs, amount=-3, side=Side.LEFT, kind=Kind.TANGENT, closed=False
        )

        show_object(res, name="splitted")
        show_object(
            sew_line.split(tool=Plane.YZ.offset(45)),
            name="sew_line",
        )


t = Wallet()
t.ext_panel()
