import math
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from furniture.geometry import Rect
from coldtype.pens import OutlinePen

try:
    from pathops import Path, OpBuilder, PathOp
except:
    pass


class DATPen(RecordingPen):
    def __init__(self, **kwargs):
        super().__init__()
        self.attrs = kwargs
    
    def addAttrs(self, **kwargs):
        self.attrs = {**self.attrs, **kwargs}
    
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

    def bounds(self):
        cbp = ControlBoundsPen(None)
        self.replay(cbp)
        mnx, mny, mxx, mxy = cbp.bounds
        return Rect((mnx, mny, mxx - mnx, mxy - mny))
    
    def align(self, rect, x="C", y="C"):
        b = self.bounds()

        if x == "C":
            xoff = -b.x + rect.x + rect.w/2 - b.w/2
        elif x == "W":
            xoff = self.rect.x
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
    
    def outline(self, pen, offset=1):
        op = OutlinePen(None, offset=offset, optimizeCurve=True)
        pen.replay(op)
        op.drawSettings(drawInner=True, drawOuter=True)
        g = op.getGlyph()
        g.draw(self)
    
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
    dt = DATPen()
    dt.rect(Rect((0, 0, 500, 500)))
    print(dt.value)