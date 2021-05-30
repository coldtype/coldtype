from drafting.geometry.primitives import calc_angle
from drafting.geometry.geometrical import Geometrical
from drafting.geometry.atom import Atom
from drafting.geometry.point import Point
from drafting.geometry.line import Line
from drafting.geometry.curve import Curve
from drafting.geometry.edge import Edge, txt_to_edge
from drafting.geometry.rect import Rect, align


def Geo(*args):
    if len(args) == 1:
        return Atom(args[0])
    elif len(args) == 2:
        if isinstance(args[0], Point):
            return Line(*args)
        else:
            return Point(*args)
    elif len(args) == 4:
        return Rect(*args)