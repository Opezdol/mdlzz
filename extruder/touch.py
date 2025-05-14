from build123d import (
    Align,
    Axis,
    Box,
    JernArc,
    Keep,
    Line,
    Mode,
    Pos,
    Rot,
    chamfer,
    extrude,
    RectangleRounded,
    Part,
    Rectangle,
    Plane,
    fillet,
    make_face,
    Vector,
    mirror,
    split,
    Circle,
)
from dataclasses import dataclass


@dataclass
class Bl_Touch:
    fix_len = 26
    fix_wid = 11.55
    fix_r = 3.2 / 2
    fix_inter = 18
    fix_round = 4
    neck_r = 11 / 2
    height = 36.3
    nozzle_offset = 7

    def sel_bottom(self, obj):
        return Plane(obj.faces().sort_by().first)

    @property
    def body(self):
        ### Sketch of top plate
        #
        l1 = Line([(0, self.fix_wid / 2), (3, self.fix_wid / 2)])
        start_arc = Vector(9, 4)
        l2 = Line(l1 @ 1, start_arc)
        l3 = JernArc(
            start=start_arc, tangent=(start_arc - l1 @ 1), radius=4, arc_size=-180
        )
        l4 = Line(l3 @ 1, (0, -3))
        l5 = Line(l4 @ 1, l1 @ 0)

        sk = make_face([l1, l2, l3, l4, l5])
        # cut
        sk = split(sk, bisect_by=Plane.XZ, keep=Keep.BOTTOM)
        # mirror
        sk += mirror(sk, about=Plane.XZ, mode=Mode.ADD)
        # cut fix
        sk -= Pos(9, 0) * Circle(self.fix_r)
        sk += mirror(sk, about=Plane.YZ, mode=Mode.ADD)

        res = extrude(sk, amount=-2.3)
        ##############
        # Make neck
        ###
        bottom = Plane(res.faces().sort_by().first)
        res += extrude(bottom * Circle(self.neck_r), amount=7.7)
        ########
        # make body
        bott = self.sel_bottom(res)
        sk = RectangleRounded(width=13, height=self.fix_wid, radius=3)
        res += extrude(bott * sk, amount=26.3)
        res = chamfer(res.edges().group_by(Axis.Z)[0], length=3)
        return Rot(Z=90) * Pos(Z=self.height) * res


#
# touch = Bl_Touch()
# show_object(touch.body)
