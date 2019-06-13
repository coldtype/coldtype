from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from furniture.geometry import Rect
from coldtype.pens import OutlinePen


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
        self.lineTo(rect.point("NW").xy())
        self.lineTo(rect.point("NE").xy())
        self.lineTo(rect.point("SE").xy())
        self.closePath()
    
    def line(self, points):
        self.moveTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        self.endPath()
    
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
    
    def oval(self, rect):
        self.roundedRect(rect, 0.5, 0.5)

if __name__ == "__main__":
    dt = DATPen()
    dt.rect(Rect((0, 0, 500, 500)))
    print(dt.value)