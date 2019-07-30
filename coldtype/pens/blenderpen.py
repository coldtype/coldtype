import os
import sys
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, Point
from fontTools.pens.basePen import BasePen

import math
try:
    import bpy
    from mathutils import Vector, Matrix
except:
    pass


def b3d_vector(pt, z=0):
    x, y = pt
    return Vector((x, y, z))


class BlenderPen(BasePen):
    def __init__(self, dat):
        super().__init__(None)
        self._spline = None
        self.splines = []
        self.dat = dat
        dat.replay(self)
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
    
    def _moveTo(self, p):
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
        self._spline = []
        self._spline.append(["BEZIER", "start", [p, p, p]])

    def _lineTo(self, p):
        self._spline.append(["BEZIER", "curve", [p, p, p]])

    def _curveToOne(self, p1, p2, p3):
        self._spline[-1][-1][-1] = p1
        self._spline.append(["BEZIER", "curve", [p2, p3, p3]])

    def _qCurveToOne(self, p1, p2):
        print("NOT SUPPORTED")

    def _closePath(self):
        if self._spline and len(self._spline) > 0 and self._spline not in self.splines:
            self.splines.append(self._spline)
            self.spline = None
        self.spline = None

    def drawOnBezierCurve(self, bez, cyclic=True):
        for spline in reversed(bez.splines): # clear existing splines
            bez.splines.remove(spline)

        for spline_data in self.splines:
            bez.splines.new('BEZIER')
            spline = bez.splines[-1]
            spline.use_cyclic_u = cyclic
            for i, (t, style, pts) in enumerate(spline_data):
                l, c, r = pts
                if i > 0:
                    spline.bezier_points.add(1)
                pt = spline.bezier_points[-1]
                pt.co = b3d_vector(c)
                pt.handle_left = b3d_vector(l)
                pt.handle_right = b3d_vector(r)

if __name__ == "__main__":
    sys.path.insert(0, os.path.realpath("."))
    from coldtype.pens.datpen import DATPen

    dp1 = DATPen()
    dp1.oval(Rect(0, 0, 500, 500).inset(200, 200))
    bp = BlenderPen(dp1)
    print(bp.splines)