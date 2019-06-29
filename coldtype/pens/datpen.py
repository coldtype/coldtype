import math
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from pathops import Path, OpBuilder, PathOp
from fontPens.flattenPen import FlattenPen

import os
import sys
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/../..")
from coldtype.geometry import Rect

try:
    from coldtype.pens.outlinepen import OutlinePen
except:
    pass


class DATPen(RecordingPen):
    def __init__(self, **kwargs):
        super().__init__()
        self.attrs = kwargs
        self.frame = None
    
    def addAttrs(self, **kwargs):
        self.attrs = {**self.attrs, **kwargs}
        return self
    
    def addFrame(self, frame):
        self.frame = frame
        return self
    
    def transform(self, transform):
        op = RecordingPen()
        tp = TransformPen(op, transform)
        self.replay(tp)
        self.value = op.value
        return self
    
    def _pathop(self, otherPen=None, operation=PathOp.XOR):
        p1 = Path()
        self.replay(p1.getPen())
        if otherPen:
            p2 = Path()
            otherPen.replay(p2.getPen())
        builder = OpBuilder(fix_winding=False, keep_starting_points=False)
        builder.add(p1, PathOp.UNION)
        if otherPen:
            builder.add(p2, operation)
        result = builder.resolve()
        d0 = DATPen()
        result.draw(d0)
        self.value = d0.value
        return self
    
    def difference(self, otherPen):
        return self._pathop(otherPen=otherPen, operation=PathOp.DIFFERENCE)
    
    def union(self, otherPen):
        return self._pathop(otherPen=otherPen, operation=PathOp.UNION)
    
    def xor(self, otherPen):
        return self._pathop(otherPen=otherPen, operation=PathOp.XOR)
    
    def reverseDifference(self, otherPen):
        return self._pathop(otherPen=otherPen, operation=PathOp.REVERSE_DIFFERENCE)
    
    def intersection(self, otherPen):
        return self._pathop(otherPen=otherPen, operation=PathOp.INTERSECTION)
    
    def removeOverlap(self):
        return self._pathop()
    
    def translate(self, x, y):
        return self.transform((1, 0, 0, 1, x, y))
    
    def scale(self, scaleX, scaleY=None, center=None):
        # TODO centering
        t = Transform().scale(scaleX, scaleY or scaleX)
        return self.transform(t)
    
    def rotate(self, degrees, point=None):
        t = Transform()
        if not point:
            point = self.bounds().point("C")
        t = t.translate(point.x, point.y)
        t = t.rotate(math.radians(degrees))
        t = t.translate(-point.x, -point.y)
        return self.transform(t)

    def bounds(self):
        cbp = ControlBoundsPen(None)
        self.replay(cbp)
        mnx, mny, mxx, mxy = cbp.bounds
        return Rect((mnx, mny, mxx - mnx, mxy - mny))
    
    def align(self, rect, x="C", y="C", bounds=False):
        if self.frame and not bounds:
            b = self.frame
        else:
            b = self.bounds()

        if x == "C":
            xoff = -b.x + rect.x + rect.w/2 - b.w/2
        elif x == "W":
            xoff = rect.x
        elif x == "E":
            xoff = -b.x + rect.x + rect.w - b.w
        
        if y == "C":
            yoff = -b.y + rect.y + rect.h/2 - b.h/2
        elif y == "N":
            yoff = rect.y + rect.h - b.h
        elif y == "S":
            yoff = rect.y
        
        diff = rect.w - b.w
        return self.translate(xoff, yoff)
        #rp2 = DATPen()
        #tp = TransformPen(rp2, (1, 0, 0, 1, xoff, yoff))
        #rp.replay(tp)
        #self._final_offset = (xoff, yoff)

    def round(self, rounding):
        rounded = []
        for t, pts in self.value:
            rounded.append(
                (t,
                [(round(x, rounding), round(y, rounding)) for x, y in pts]))
        self.value = rounded
        return self

    def record(self, pen):
        pen.replay(self)
        return self
    
    def glyph(self, glyph):
        glyph.draw(self)
        return self

    def flatten(self):
        dp = DATPen()
        fp = FlattenPen(dp, approximateSegmentLength=4, segmentLines=True)
        self.replay(fp)
        self.value = dp.value
        return self
    
    def outline(self, offset=1):
        op = OutlinePen(None, offset=offset, optimizeCurve=True)
        self.replay(op)
        op.drawSettings(drawInner=True, drawOuter=True)
        g = op.getGlyph()
        p = DATPen()
        g.draw(p)
        self.value = p.value
        return self
    
    def dots(self, radius=4):
        dp = DATPen()
        for t, pts in self.value:
            if t == "moveTo":
                x, y = pts[0]
                dp.oval(Rect((x-radius, y-radius, radius, radius)))
        self.value = dp.value
        return self
    
    def catmull(self, points):
        p0 = points[0]
        p1, p2, p3 = points[:3]
        pts = [p0]

        i = 1
        while i < len(points):
            pts.append([
                ((-p0[0] + 6 * p1[0] + p2[0]) / 6),
                ((-p0[1] + 6 * p1[1] + p2[1]) / 6),
                ((p1[0] + 6 * p2[0] - p3[0]) / 6),
                ((p1[1] + 6 * p2[1] - p3[1]) / 6),
                p2[0],
                p2[1]
            ])

            p0 = p1
            p1 = p2
            p2 = p3
            try:
                p3 = points[i + 2]
            except:
                p3 = p3

            i += 1

        self.moveTo(pts[0])
        for p in pts[1:]:
            self.curveTo((p[0], p[1]), (p[2], p[3]), (p[4], p[5]))
        #self.closePath()
    
    def pattern(self, rect, clip=False):
        dp_copy = DATPen()
        dp_copy.value = self.value

        for y in range(-1, 1):
            for x in range(-1, 1):
                dpp = DATPen()
                dp_copy.replay(dpp)
                dpp.translate(rect.w*x, rect.h*y)
                dpp.replay(self)
        
        self.translate(rect.w/2, rect.h/2)
        if clip:
            clip_box = DATPen().rect(rect)
            return self.intersection(clip_box)
        return self
    
    def rect(self, rect):
        self.moveTo(rect.point("SW").xy())
        self.lineTo(rect.point("SE").xy())
        self.lineTo(rect.point("NE").xy())
        self.lineTo(rect.point("NW").xy())
        self.closePath()
        return self

    def line(self, points):
        self.moveTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        self.endPath()
        return self
    
    def roundedRect(self, rect, hr, vr):
        l, b, w, h = rect
        r, t = l + w, b + h
        K = 4 * (math.sqrt(2)-1) / 3
        if hr <= 0.5:
            hr = w * hr
        if vr <= 0.5:
            vr = h * vr
        self.moveTo((l + hr, b))
        self.lineTo((r - hr, b))
        self.curveTo((r+hr*(K-1), b), (r, b+vr*(1-K)), (r, b+vr))
        self.lineTo((r, t-vr))
        self.curveTo((r, t-vr*(1-K)), (r-hr*(1-K), t), (r-hr, t))
        self.lineTo((l+hr, t))
        self.curveTo((l+hr*(1-K), t), (l, t-vr*(1-K)), (l, t-vr))
        self.lineTo((l, b+vr))
        self.curveTo((l, b+vr*(1-K)), (l+hr*(1-K), b), (l+hr, b))
        self.closePath()
        return self
    
    def oval(self, rect):
        self.roundedRect(rect, 0.5, 0.5)
        return self


if __name__ == "__main__":
    dt = DATPen(fill=[1,2,3])
    dt.rect(Rect((0, 0, 500, 500)))
    #dt.outline()
    print(dt.value)