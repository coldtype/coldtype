import math

from fontPens.marginPen import MarginPen
from fontTools.misc.transform import Transform

from coldtype.geometry import Line
from coldtype.beziers import CurveCutter, CurveSample, splitCubicAtT, calcCubicArcLength


class SegmentingMixin():
    def distribute_on_path(self,
        path,
        offset=0,
        cc=None,
        notfound=None,
        center=False
        ):
        if len(self) == 0:
            # TODO print error?
            return self

        if cc:
            cutter = cc
        else:
            cutter = CurveCutter(path)
        if center is not False:
            offset = (cutter.length-self.bounds().w)/2 + center
        limit = len(self._els)
        for idx, p in enumerate(self._els):
            f = p.ambit()
            bs = f.y
            ow = offset + f.x + f.w / 2
            #if ow < 0:
            #    if notfound:
            #        notfound(p)
            if ow > cutter.length:
                limit = min(idx, limit)
            else:
                _p, tangent = cutter.subsegmentPoint(end=ow)
                x_shift = bs * math.cos(math.radians(tangent))
                y_shift = bs * math.sin(math.radians(tangent))
                t = Transform()
                t = t.translate(_p[0] + x_shift - f.x, _p[1] + y_shift - f.y)
                t = t.translate(f.x, f.y)
                t = t.rotate(math.radians(tangent-90))
                t = t.translate(-f.x, -f.y)
                t = t.translate(-f.w*0.5)
                p.transform(t)

        if limit < len(self._els):
            self._els = self._els[0:limit]
        return self
    
    distributeOnPath = distribute_on_path

    def subsegment(self, start=0, end=1):
        """Return a subsegment of the pen based on `t` values `start` and `end`"""
        if not self.val_present():
            return
        
        cc = CurveCutter(self)
        start = 0
        end = end * cc.calcCurveLength()
        pv = cc.subsegment(start, end)
        self._val.value = pv
        return self
    
    def point_t(self, t=0.5):
        """Get point value for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        p, tangent = cc.subsegmentPoint(start=0, end=tv)
        return p, tangent
    
    def split_t(self, t=0.5):
        if not self.val_present():
            return

        a = self._val.value[0][-1][0]
        b, c, d = self._val.value[-1][-1]
        return splitCubicAtT(a, b, c, d, t)
    
    def add_pt_t(self, cuidx, t):
        if not self.val_present():
            return

        cidx = 0
        insert_idx = -1
        c1, c2 = None, None

        for idx, (mv, pts) in enumerate(self._val.value):
            if mv == "curveTo":
                if cidx == cuidx:
                    insert_idx = idx
                    a = self._val.value[idx-1][-1][-1]
                    b, c, d = pts
                    c1, c2 = splitCubicAtT(a, b, c, d, t)
                cidx += 1
            elif mv == "lineTo":
                if cidx == cuidx:
                    insert_idx = idx
                    a = self._val.value[idx-1][-1][-1]
                    b = pts[0]
                    l = Line(a, b)
                    c1 = [l.t(0.5)]
                    c2 = [b]
                cidx += 1
        
        if c2:
            if len(c2) > 1:
                self._val.value[insert_idx] = ("curveTo", c1[1:])
                self._val.value.insert(insert_idx+1, ("curveTo", c2[1:]))
            else:
                self._val.value[insert_idx] = ("lineTo", c1)
                self._val.value.insert(insert_idx+1, ("lineTo", c2))
        return self
    
    def samples(self, interval=10, even=False):
        cc = CurveCutter(self)
        samples = []
        length = cc.calcCurveLength()
        inc = 1
        idx = 0
        while inc < length:
            pt, tan = cc.subsegmentPoint(start=0, end=inc)
            samples.append(CurveSample(idx, pt, inc / length, tan))
            inc += interval
            idx += 1
        
        for i, s in enumerate(samples):
            next = samples[i+1] if i < len(samples)-1 else s
            prev = samples[i-1] if i > 0 else s
            s.neighbors(prev, next)
        
        return samples
    
    def onSamples(self, interval=10, even=False, fn=None):
        return (type(self)().enumerate(self.samples(interval=interval, even=even), lambda s: fn(self, s)))
    
    def length(self, t=1):
        """Get the length of the curve for time `t`"""
        cc = CurveCutter(self)
        start = 0
        tv = t * cc.calcCurveLength()
        return tv
    
    def ease_t(self, e, tries=0):
        _, _, w, h = self.ambit()
        pen = MarginPen(None, e*w, isHorizontal=False)
        self.replay(pen)
        try:
            return pen.getAll()[0]/h
        except IndexError:
            # HACK for now but I guess works?
            #print("INDEX ERROR", e)
            if tries < 500:
                return self.ease_t(e-0.01, tries=tries+1)
            return 0
        
    def divide(self, length=150, floor=True, count=None, idx=0, max=None):
        a = self.v.value[0][-1][-1]
        b, c, d = self.v.value[1][-1]
        l = calcCubicArcLength(a, b, c, d)

        if count is not None:
            length = l / count
            floor = False

        if l < length:
            if max is not None and len(self.v.value) < max:
                self.add_pt_t(0, 0.5)
                self.divide(length=length, floor=False, idx=idx+1, max=max)
            return self
        
        if max is not None and len(self.v.value) >= max:
            return self

        if floor:
            fl = math.floor(l/length)
            length = l/fl
        
        t = 1/(l/length)
        
        if l > length*1.5:
            self.add_pt_t(0, 1-t)
            self.divide(length=length, floor=False, idx=idx+1, max=max)
        elif max is not None:
            self.add_pt_t(0, 0.5)
            self.divide(length=length, floor=False, idx=idx+1, max=max)
            pass
        return self