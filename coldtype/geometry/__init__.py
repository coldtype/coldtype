from coldtype.geometry.primitives import calc_angle
from coldtype.geometry.geometrical import Geometrical
from coldtype.geometry.atom import Atom
from coldtype.geometry.point import Point
from coldtype.geometry.line import Line
from coldtype.geometry.curve import Curve
from coldtype.geometry.edge import Edge, txt_to_edge
from coldtype.geometry.rect import Rect, align


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