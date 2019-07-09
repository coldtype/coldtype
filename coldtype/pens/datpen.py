import math
from fontTools.pens.filterPen import ContourFilterPen
from fontTools.pens.boundsPen import ControlBoundsPen, BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from pathops import Path, OpBuilder, PathOp
from fontPens.flattenPen import FlattenPen
from grapefruit import Color
from random import random, randint
from fontTools.misc.bezierTools import calcCubicArcLength, splitCubicAtT


if __name__ == "__main__":
    import os
    import sys
    dirname = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{dirname}/../..")

from coldtype.geometry import Rect, Edge, txt_to_edge
from coldtype.pens.drawablepen import Gradient, normalize_color


try:
    from coldtype.pens.outlinepen import OutlinePen
except:
    pass


class SmoothPointsPen(ContourFilterPen):
    def __init__(self, outPen, length=80):
        super().__init__(outPen)
        self.length = length

    def filterContour(self, contour):
        nc = []

        def split(pts):
            p0, p1, p2, p3 = pts
            length_arc = calcCubicArcLength(p0, p1, p2, p3)
            if length_arc <= self.length:
                nc.append([t, pts[1:]])
            else:
                d = self.length / length_arc
                b = (p0, p1, p2, p3)
                a, b = splitCubicAtT(*b, d)
                nc.append([t, a[1:]])
                #nc.append([t, b[1:]])
                split(b)

        for i, (t, pts) in enumerate(contour):
            if t == "curveTo":
                p1, p2, p3 = pts
                p0 = contour[i-1][-1][-1]
                split((p0, p1, p2, p3))
                #length_arc = calcCubicArcLength(p0, p1, p2, p3)
                #if length_arc <= self.length:
                #    nc.append([t, pts])
                #else:
                #    d = self.length / length_arc
                #    b = (p0, p1, p2, p3)
                #    for x in range(1):
                #        a, b = splitCubicAtT(*b, d)
                #        nc.append([t, a[1:]])
                #        nc.append([t, b[1:]])
                #        length_arc = calcCubicArcLength(*b)
                    
            else:
                nc.append([t, pts])
        return nc


class DATPen(RecordingPen):
    def __init__(self, **kwargs):
        super().__init__()
        self.attrs = {}
        self.addAttrs(fill=(1, 0, 0.5))
        self.addAttrs(**kwargs)
        self.frame = None
        self.typographic = False
    
    def addAttrs(self, **kwargs):
        for k, v in kwargs.items():
            if k == "fill":
                self.attrs[k] = normalize_color(v)
            elif k == "stroke":
                if not isinstance(v, dict):
                    self.attrs[k] = dict(color=normalize_color(v))
                else:
                    self.attrs[k] = dict(weight=v.get("weight", 1), color=normalize_color(v.get("color", 0)))
            else:
                self.attrs[k] = v
        return self
    
    def addFrame(self, frame):
        self.frame = frame
        return self
    
    def getFrame(self):
        if self.frame:
            return self.frame
        else:
            return self.bounds()
    
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
        return self._pathop(otherPen=DATPen(), operation=PathOp.UNION)
    
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
    
    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, bounds=False):
        x = txt_to_edge(x)
        y = txt_to_edge(y)
        
        if self.frame and not bounds:
            b = self.frame
        else:
            b = self.bounds()

        if x == Edge.CenterX:
            xoff = -b.x + rect.x + rect.w/2 - b.w/2
        elif x == Edge.MinX:
            xoff = rect.x
        elif x == Edge.MaxX:
            xoff = -b.x + rect.x + rect.w - b.w
        
        if y == Edge.CenterY:
            yoff = -b.y + rect.y + rect.h/2 - b.h/2
        elif y == Edge.MaxY:
            yoff = rect.y + rect.h - b.h
        elif y == Edge.MinY:
            yoff = rect.y
        
        diff = rect.w - b.w
        return self.translate(xoff, yoff)

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

    def flatten(self, length=10):
        if length == 0:
            return self
        dp = DATPen()
        fp = FlattenPen(dp, approximateSegmentLength=length, segmentLines=True)
        self.replay(fp)
        self.value = dp.value
        return self
    
    def addSmoothPoints(self, length=100):
        rp = RecordingPen()
        fp = SmoothPointsPen(rp)
        self.replay(fp)
        self.value = rp.value
        return self
    
    def roughen(self, length=10, amplitude=10, threshold=10):
        #self.flatten(length=length)
        randomized = []
        for t, pts in self.value:
            if t == "lineTo" or t == "curveTo":
                jx = randint(0, amplitude) - amplitude/2
                jy = randint(0, amplitude) - amplitude/2
                randomized.append([t, [(x+jx, y+jy) for x, y in pts]])
            else:
                randomized.append([t, pts])
        self.value = randomized
        return self
        mod_value = []
        for t, vals in recorder.value:
            amp = randint(0, amplitude)
            if t == "lineTo" and len(vals) > 0:
                x, y = vals[0]
                jx = floor(x + randint(0, amp) - amp/2)
                jy = floor(y + randint(0, amp) - amp/2)
                vals = [(jx, jy)]
                mod_value.append([t, vals])
            else:
                mod_value.append([t, vals])

        recorder.value = mod_value

        r2 = RecordingPen()
        tpen = ThresholdPen(r2, threshold=threshold)
        recorder.replay(tpen)

        r2.replay(bpr)
        return bp.intersection(bpr)
    
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
        if isinstance(rect, Rect):
            self.moveTo(rect.point("SW").xy())
            self.lineTo(rect.point("SE").xy())
            self.lineTo(rect.point("NE").xy())
            self.lineTo(rect.point("NW").xy())
            self.closePath()
        elif isinstance(rect[0], Rect):
            for r in rect:
                self.rect(r)
        else:
            self.rect(Rect(rect))
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
    
    def polygon(self, sides, rect):
        radius = rect.square().w / 2
        c = rect.center()
        one_segment = math.pi * 2 / sides
        points = [(math.sin(one_segment * i) * radius, math.cos(one_segment * i) * radius) for i in range(sides)]
        self.moveTo(points[0])
        for p in points[1:]:
            self.lineTo(p)
        self.closePath()
        self.align(rect)
        return self
    
    def skeleton(self, scale=1):
        dp = DATPen()
        for t, pts in self.value:
            if t == "moveTo":
                r = 12*scale
                x, y = pts[0]
                dp.rect(Rect((x-r/2, y-r/2, r, r)))
            elif t == "curveTo":
                r = 6*scale
                x, y = pts[-1]
                dp.oval(Rect((x-r/2, y-r/2, r, r)))
                r = 4*scale
                x, y = pts[1]
                dp.oval(Rect((x-r/2, y-r/2, r, r)))
                x, y = pts[0]
                dp.oval(Rect((x-r/2, y-r/2, r, r)))
            elif t == "lineTo":
                r = 6*scale
                x, y = pts[0]
                dp.rect(Rect((x-r/2, y-r/2, r, r)))
        return dp


class DATPenSet():
    def __init__(self, *pens):
        self.pens = []
        self.addPens(pens)
    
    def addPens(self, pens):
        for p in pens:
            if isinstance(p, DATPen):
                self.pens.append(p)
            else:
                self.addPens(p)

    def align(self, rect, x=Edge.CenterX, y=Edge.CenterY, typographicBaseline=True):
        # split up the space according to the bounds of the individual pens
        # then call the align method of each one individually
        frames = []
        for p in self.pens:
            frames.append(p.getFrame())
        w = sum([f.w for f in frames])
        
        if isinstance(rect, Rect):
            _r = rect.take(w, x).subdivide([f.w for f in frames], Edge.MinX)
        else:
            _r = rect
        
        if typographicBaseline:
            mxh = max([f.h for f in frames])
            for p in self.pens:
                if p.typographic:
                    p.frame.h = mxh

        for idx, p in enumerate(self.pens):
            p.align(_r[idx], x, y)


if __name__ == "__main__":
    from coldtype.viewer import viewer
    from coldtype.pens.svgpen import SVGPen
    from grapefruit import Color

    from coldtype import StyledString
    
    with viewer() as v:
        r = Rect((0, 0, 500, 500))
        ss1 = StyledString("Hello", "≈/Nonplus-Black.otf", fontSize=200, varyFontSize=True)
        #ss1.fit(r.w)
        dp1 = ss1.asDAT().align(r)
        #dp1.addSmoothPoints()
        #dp1.roughen()
        #dp1.roughen(length=20, amplitude=4)
        dp1.removeOverlap()
        dp2 = DATPen(fill=None, stroke=("random", 0.5)).record(dp1)
        #dp1 = dp1.skeleton(scale=3)
        dp1.addAttrs(fill=Gradient.Horizontal(r, ("random", 0.75), ("random", 0.75)))
        #dp1.addAttrs(fill=("random", 0.15), stroke=("random", 0.8))
        dt1 = DATPen(fill=Gradient.Vertical(r, ("random", 0.5), ("random", 0.5)), stroke=dict(color=("random", 0.5), weight=10))
        dt1.oval(r.inset(100, 100))
        dt2 = DATPen(fill=Gradient.Vertical(r, ("random", 0.5), ("random", 0.5)))
        dt2.rect(r.inset(100, 100))
        dt2.align(r)
        dt3 = DATPen(fill=Gradient.Vertical(r, ("random", 0.2), ("random", 0.2))).polygon(8, r)
        dt3.rotate(120)
        v.send(SVGPen.Composite([
            #dt1,
            #dt2,
            #dt3,
            dp1,
            #dp2,
            ], r), r)