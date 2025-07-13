from build123d import Circle, extrude, Sketch, Plane, loft
from dataclasses import dataclass


@dataclass
class Shinima:
    in_r: float = 78 / 2
    out_r: float = 109 / 2
    thick: float = 15
    incision_depth = 2
    incision_r = 100 / 2
    tot_thick = 30

    def build(self):
        sk_l = Sketch() + [
            Circle(102 / 2),
            Plane.XY.offset(self.tot_thick) * Circle(self.out_r),
        ]
        res = loft(sk_l)
        minus_body = extrude(Circle(self.in_r), amount=self.tot_thick + 2)
        # res = extrude(sk, amount=self.tot_thick)
        minus = extrude(Circle(self.incision_r), amount=self.incision_depth)
        return res - minus - minus_body


t = Shinima()
show_object(t.build(), name="huin")
