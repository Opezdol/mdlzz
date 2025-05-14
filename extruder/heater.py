from build123d import (
    GridLocations,
    Plane,
    RegularPolygon,
    Sketch,
    Wire,
    chamfer,
    extrude,
    RectangleRounded,
    Circle,
    SlotOverall,
    Part,
    Pos,
    Hole,
)

from dataclasses import dataclass, field


@dataclass
class DragonUHF:
    tiny: float = 0.1
    r: float = 22 / 2
    slot_width = 21.4
    radiator_height = 26
    top_thick = 3.5
    fix_dimention = 11.5
    fix_thick_lower = 2.4
    heater_block1 = 7.82
    heater_block2 = 12.5
    heater_UHF = 8
    heater_nozzle = 5
    # Build selection
    simple: bool = field(default=False)

    @property
    def height(self):
        return (
            self.radiator_height
            + self.fix_thick_lower
            + self.heater_block1
            + self.heater_block2
            + self.heater_UHF
            + self.heater_nozzle
        )

    def _slot_body(self, slot_width, plane) -> Part:
        slot = (
            plane
            * Pos(
                Y=self.radiator_height - slot_width / 2 - self.top_thick
            )  # 3.5mm from top, slot begins
            * extrude(
                SlotOverall(width=slot_width, height=9, rotation=90),
                amount=self.r + self.tiny,
                both=True,
            )
        )
        return slot

    @property
    def fix(self):
        return GridLocations(
            x_spacing=self.fix_dimention,
            y_spacing=self.fix_dimention,
            x_count=2,
            y_count=2,
        )

    def _chiller_simple(self) -> Part:
        base = extrude(
            Circle(radius=self.r + self.tiny),
            amount=self.radiator_height + self.fix_thick_lower,
        )
        return base

    def chiller(self) -> Part:
        """Creates main body of chiller &&  creates new properties for future usage
        x_wire & y_wire
        """
        ## if we need simple model for boolean..
        if self.simple:
            return Plane.XY.offset(-self.fix_thick_lower) * self._chiller_simple()
        ## else we build complex model.

        base = extrude(Circle(radius=self.r + self.tiny), amount=self.radiator_height)
        top_face = Plane(base.faces().sort_by().last)
        # Top holes for filemant and PTFE tube
        base -= top_face * extrude(Circle(radius=2), amount=-1)
        base -= top_face * extrude(Circle(radius=1.8 / 2), amount=-10)
        # make fixes
        base -= [top_face * loc * Hole(radius=1, depth=3) for loc in self.fix]

        # closed slot
        # ___________________________________________
        base -= self._slot_body(self.slot_width, Plane.YZ)
        # opened slot for thermistor and heater block
        # ___________________________________________
        base -= self._slot_body(self.slot_width + 4, Plane.XZ)
        # ___________________________________________
        #       CHAMFER ZONE
        # selction based on proportions. Just testing
        # chamfer X axis. slots
        edges_to_chamfer = base.edges().filter_by(
            lambda e: (e.center().X > self.r * 0.8 or e.center().X < -self.r * 0.8)
            and self.radiator_height * 0.05 < e.center().Z < self.radiator_height * 0.92
        )
        # x_wire CREATED. VERY BAD FUNCITON CONSTRUCTION!!
        # create new property for future use
        self.x_wire = Wire(edges_to_chamfer[0:6])
        res = chamfer(edges_to_chamfer, length=0.9)
        # ___________________________________________
        # chamfer Y axis. slots
        edges_to_chamfer = res.edges().filter_by(
            lambda e: (e.center().Y > self.r * 0.8 or e.center().Y < -self.r * 0.8)
            and e.center().Z < self.radiator_height * 0.92
        )
        # y_wire CREATED. VERY BAD FUNCITON CONSTRUCTION!!
        # create new property for future use for Y axis
        self.y_wire = Wire(edges_to_chamfer[0:5])
        res = chamfer(edges_to_chamfer, length=0.9)
        # ___________________________________________
        # add fixes for heater from bottom
        sk = Sketch() + [loc * Circle(radius=1) for loc in self.fix]
        res += extrude(sk, amount=-self.fix_thick_lower)
        return res

    def heater(self, at_plane=Plane.XY):
        res = extrude(
            RectangleRounded(width=21, height=19, radius=3), amount=-self.heater_block1
        )
        low_face = res.faces().sort_by().first

        res += extrude(
            Plane(low_face) * RectangleRounded(width=21, height=8.7, radius=2),
            amount=self.heater_block2,
        )
        # additional heater for high flow
        res += extrude(
            Plane(res.faces().sort_by().first)
            * RegularPolygon(radius=5.5, side_count=6),
            amount=self.heater_UHF,
        )
        res += chamfer(
            extrude(
                Plane(res.faces().sort_by().first)
                * RegularPolygon(radius=2, side_count=6),
                amount=self.heater_nozzle,
            )
            .edges()
            .sort_by()[:6],
            1,
        )

        return at_plane * res

    @property
    def body(self):
        res = self.chiller()
        res += self.heater(at_plane=Plane.XY.offset(-self.fix_thick_lower))
        # print(self.y_wire.is_closed)
        # show_object(self.x_wire, name="x_wire")
        # show_object(self.y_wire, name="y_wire")
        return res


# res = Heater()
# show_object(res.body)
