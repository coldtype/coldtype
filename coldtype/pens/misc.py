from enum import Enum
from fontTools.pens.filterPen import ContourFilterPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.misc.bezierTools import splitCubicAtT, calcCubicArcLength


USE_SKIA_PATHOPS = True

try:
    from pathops import Path, OpBuilder, PathOp
except ImportError:
    USE_SKIA_PATHOPS = False

try:
    from booleanOperations.booleanGlyph import BooleanGlyph
    from booleanOperations.exceptions import UnsupportedContourError
except ImportError:
    if not USE_SKIA_PATHOPS:
        print(">>> NO PATHOPS FOUND; please install either skia-pathops or booleanOperations")


class BooleanOp(Enum):
    Difference = 0
    Union = 1
    XOR = 2
    ReverseDifference = 3
    Intersection = 4
    Simplify = 5

    def Skia(x):
        return [
            PathOp.DIFFERENCE,
            PathOp.UNION,
            PathOp.XOR,
            PathOp.REVERSE_DIFFERENCE,
            PathOp.INTERSECTION,
        ][x.value]
    
    def BooleanGlyphMethod(x):
        return [
            "difference",
            "union",
            "xor",
            "reverseDifference",
            "intersection",
        ][x.value]


def calculate_pathop(pen1, pen2, operation):
    if USE_SKIA_PATHOPS:
        p1 = Path()
        pen1.replay(p1.getPen())
        if operation == BooleanOp.Simplify:
            # ignore pen2
            p1.simplify(fix_winding=True, keep_starting_points=True)
            d0 = RecordingPen()
            p1.draw(d0)
            return d0.value
        if pen2:
            p2 = Path()
            pen2.replay(p2.getPen())
        builder = OpBuilder(fix_winding=True, keep_starting_points=True)
        builder.add(p1, PathOp.UNION)
        if pen2:
            builder.add(p2, BooleanOp.Skia(operation))
        result = builder.resolve()
        d0 = RecordingPen()
        result.draw(d0)
        return d0.value
    else:
        bg = BooleanGlyph()
        pen1.replay(bg.getPen())
        if operation == BooleanOp.Simplify:
            # ignore pen2
            try:
                bg = bg.removeOverlap()
            except UnsupportedContourError:
                print("booleanOperations could not removeOverlap (qcurve present)")
                pass
            dp = RecordingPen()
            bg.draw(dp)
            return dp.value

        bg2 = BooleanGlyph()
        if pen2:
            pen2.replay(bg2.getPen())
        bg = bg._booleanMath(BooleanOp.BooleanGlyphMethod(operation), bg2)
        dp = RecordingPen()
        bg.draw(dp)
        return dp.value


class ExplodingPen(ContourFilterPen):
    def __init__(self, outPen):
        self._pens = []
        super().__init__(outPen)

    def filterContour(self, contour):
        self._pens.append(contour)
        return contour


class SmoothPointsPen(ContourFilterPen):
    def __init__(self, outPen, length=80):
        super().__init__(outPen)
        self.length = length

    def filterContour(self, contour):
        nc = []

        def split_line(pts):
            p0, p1 = pts
            nc.append(["lineTo", [p1]])

        def split_curve(pts):
            p0, p1, p2, p3 = pts
            length_arc = calcCubicArcLength(p0, p1, p2, p3)
            if length_arc <= self.length:
                nc.append(["curveTo", pts[1:]])
            else:
                d = self.length / length_arc
                b = (p0, p1, p2, p3)
                a, b = splitCubicAtT(*b, d)
                nc.append(["curveTo", a[1:]])
                split_curve(b)

        for i, (t, pts) in enumerate(contour):
            if t == "lineTo":
                p0 = contour[i-1][-1][-1]
                split_line((p0, pts[0]))
            elif t == "curveTo":
                p1, p2, p3 = pts
                p0 = contour[i-1][-1][-1]
                split_curve((p0, p1, p2, p3))
            else:
                nc.append([t, pts])
        return nc