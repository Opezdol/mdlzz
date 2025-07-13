from build123d import (
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


class Hand:
    def __init__(self) -> None:
        self.main_circle = 9 / 2
        self.main_sq = 4.2
        self.base_len = 54
        self.tot_thick = 31
        self.top_offs = 6.3
        self.w_end = 17.5
        self.w_st = 12
        self.w_angle = 8.5
        self.main_offs = 2
        self.y_cent = 45

    def base_sk(self):
        x_off = -self.main_offs - self.main_sq / 2
        ##  lines def
        l1 = Line((x_off, 0), (x_off, self.y_cent))
        l2 = Line(l1 @ 1, (-self.main_sq / 2, self.base_len))
        l3 = Line(l2 @ 1, (x_off + 10, self.base_len - 1))
        l4 = Line(l3 @ 1, (x_off + self.w_end, 0))
        l5 = Line(l4 @ 1, (x_off, 0))
        lines = Curve() + [l1, l2, l3, l4, l5]
        sk = make_face(lines)  # type: ignore
        sk = Pos(Y=-self.y_cent) * fillet(
            sk.vertices().sort_by_distance(other=(0, 0))[3:], radius=1.5
        )
        # sk = fillet(sk.vertices().sort_by_distance(other=(0, 0))[0], radius=20)
        return sk

    def build(self):
        sk = self.base_sk()
        res = extrude(sk, self.tot_thick).clean()  # type: ignore
        minus_axis = extrude(
            # Rot(Z=10)
            Pos(Z=self.tot_thick) * RectangleRounded(self.main_sq, self.main_sq, 0.3),  # type: ignore
            amount=-20,
        )
        # main incisio
        min_body_sk = Pos(Z=self.tot_thick) * ((Pos(X=-3, Y=-3) * sk) + Circle(5.2))  # type: ignore
        min_body = extrude(min_body_sk, amount=-6)  # type: ignore
        # main_minus
        main_minus_sk = Pos(Z=self.tot_thick) * (  # type: ignore
            (Pos(X=-2.5, Y=-3) * sk) - Pos(Y=1) * Rectangle(20, 12, rotation=5)
        )
        main_minus = extrude(main_minus_sk, amount=-self.tot_thick + 5)  # type: ignore
        # SPLIT by plane
        bisect_plane = Plane.XY.offset(8).rotated((5, 0, 0))
        res = split(res, bisect_by=bisect_plane)  # type: ignore
        main_minus = split(main_minus, bisect_by=bisect_plane.offset(4))  # type: ignore
        # Fillet main minus body
        # edgs = main_minus.edges().sort_by()[:4].sort_by(Axis.X)[2:].sort_by(Axis.Y)[1:]
        #
        # res_edgs = res.edges().group_by()[0]  # .sort_by(Axis.X)[5:].sort_by(Axis.Y)[1:]
        # res = fillet(res_edgs, radius=5)
        res_edgs = res.edges().sort_by(Axis.Z)[1:4]
        # edgs = main_minus.edges().sort_by(Axis.Z)[1:4]
        # show_object(edgs, name="edgs")
        # main_minus = fillet(edgs, radius=1)
        # show_object(main_minus, name="main_minus")
        # res = fillet(res_edgs, radius=2.2)

        # Minus zone
        # res -= main_minus
        edgs_minus = main_minus.edges().sort_by(Axis.Z)[2]
        edgs_base = res.edges().sort_by(Axis.Z)[2]
        res = fillet(edgs_base, 3)
        fillet_radius = 10
        res -= fillet(edgs_minus, radius=fillet_radius)
        res -= min_body
        # show_object(min_body_sk, name="min_body_sk")
        # sk_res = min_body_sk - main_minus_sk
        face = res.faces().filter_by(Axis.Z).sort_by()[0]
        face_plane = Plane(face)
        face = face - Pos(Y=1.5, X=1.5) * face
        face -= face_plane * Pos(X=-3.3) * Rectangle(2, 15)  # type: ignore
        fc_edgs = face.vertices().sort_by(Axis.Y)[2]
        face = fillet(fc_edgs, radius=2)
        # show_object(face, name="face")                                                      # type: ignore
        res += extrude(face, amount=6)  # type: ignore
        # show_object(face, name="face")
        # show_object(minus_axis, name="minus_axis")
        # show_object(res_edgs, name="res edges")
        # show_object(min_body, name="minbody")
        #  MAKE FILLETS
        ed = res.edges().filter_by(Axis.Z).sort_by(Axis.X)[2]
        show_object(ed, name="ed")
        res = fillet(ed, radius=4)
        ed = res.edges().filter_by(Axis.X).sort_by(Axis.Z)[-1]
        res = fillet(ed, radius=5)
        res -= minus_axis
        # show_object(ed, name="ed")

        return res

    def for_hand(self):

        res = self.build()
        ell = Ellipse(x_radius=23 / 2, y_radius=14 / 2, rotation=90 + 15)
        snap = res.edges()
        ell = (
            Pos(Y=-self.base_len + 25) * Rot(Y=-30) * extrude(ell, amount=30, both=True)
        )
        res -= ell
        edgs = res.edges() - snap
        res = fillet(edgs, radius=1.5)
        # show_object(edgs.sort_by(Axis.Y)[3:-3], name="edges")                               # type: ignore
        ell2 = Ellipse(x_radius=23 / 2, y_radius=14 / 2, rotation=90)
        ell2 = split(ell2, bisect_by=Plane.YZ)  # type: ignore
        ell2 = Pos(Z=15, X=11.5) * revolve(ell2, axis=Axis.Y)  # type: ignore
        res -= ell2
        # show_object(ell2, name="ellipse")                                                   # type: ignore
        return res


t = Hand()
show_object(t.build(), name="base")  # type: ignore
# show_object(t.base_sk(), name="base_sk")
# show_object(t.for_hand(), name="base")
