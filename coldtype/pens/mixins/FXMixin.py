import math
from copy import deepcopy

from fontTools.pens.recordingPen import RecordingPen
from fontPens.flattenPen import FlattenPen

from coldtype.geometry import Point
from coldtype.pens.outlinepen import OutlinePen
from coldtype.pens.translationpen import TranslationPen, polarCoord
from coldtype.pens.misc import ExplodingPen, SmoothPointsPen


class FXMixin():
    def flatten(self, length=10, segmentLines=True):
        """
        Runs a fontTools `FlattenPen` on this pen
        """
        for el in self._els:
            el.flatten(length, segmentLines)

        if self.val_present():
            rp = RecordingPen()
            fp = FlattenPen(rp, approximateSegmentLength=length, segmentLines=segmentLines)
            self.replay(fp)
            self._val.value = rp.value

        return self
    
    def smooth(self):
        for el in self._els:
            el.smooth()
        
        if self.val_present():
            rp = RecordingPen()
            fp = SmoothPointsPen(rp)
            self.replay(fp)
            self._val.value = rp.value
        
        return self
    
    def explode(self):
        """Convert all contours to individual paths"""
        for el in self._els:
            el.explode()

        if self.val_present():
            rp = RecordingPen()
            ep = ExplodingPen(rp)
            self.replay(ep)

            for p in ep._pens:
                el = type(self)()
                el._val.value = p
                el._attrs = deepcopy(self._attrs)
                self.append(el)
        
        return self
    
    def implode(self):
        # TODO preserve frame from some of this?
        #self.reset_val()
        self._val = RecordingPen()
        
        for el in self._els:
            self.record(el._val)

        self._els = []
        return self
    
    def map_points(self, fn, filter_fn=None):
        idx = 0
        for cidx, c in enumerate(self._val.value):
            move, pts = c
            pts = list(pts)
            for pidx, p in enumerate(pts):
                x, y = p
                if filter_fn and not filter_fn(Point(p)):
                    continue
                result = fn(idx, x, y)
                if result:
                    pts[pidx] = result
                idx += 1
            self._val.value[cidx] = (move, pts)
        return self
    
    def mod_contour(self, contour_index, mod_fn):
        exploded = self.explode()
        mod_fn(exploded[contour_index])
        self._val.value = exploded.implode()._val.value
        return self
    
    def repeat(self, times=1):
        for el in self._els:
            el.repeat(times)

        if self.val_present():
            copy = self.copy()._val.value
            _, copy_0_data = copy[0]
            copy[0] = ("moveTo", copy_0_data)
            self._val.value = self._val.value[:-1] + copy
            if times > 1:
                self.repeat(times-1)
        
        return self

    def outline(self,
        offset=1,
        drawInner=True,
        drawOuter=True,
        cap="square",
        miterLimit=None,
        closeOpenPaths=True
        ):
        """AKA expandStroke"""
        for el in self._els:
            el.outline(offset, drawInner, drawOuter, cap, miterLimit, closeOpenPaths)
        
        if self.val_present():
            op = OutlinePen(None
                , offset=offset
                , optimizeCurve=True
                , cap=cap
                , miterLimit=miterLimit
                , closeOpenPaths=closeOpenPaths)
            
            self._val.replay(op)
            op.drawSettings(drawInner=drawInner
                , drawOuter=drawOuter)
            g = op.getGlyph()
            self._val.value = []
            g.draw(self._val)
        
        return self
    
    ol = outline
    
    def project(self, angle, width):
        offset = polarCoord((0, 0), math.radians(angle), width)
        self.translate(offset[0], offset[1])
        return self

    def castshadow(self,
        angle=-45,
        width=100,
        ro=1,
        fill=True
        ):
        for el in self._els:
            el.castshadow(angle, width, ro, fill)
        
        if self.val_present():
            out = RecordingPen()
            tp = TranslationPen(out
                , frontAngle=angle
                , frontWidth=width)
            
            self._val.replay(tp)
            if fill:
                self.copy().project(angle, width)._val.replay(out)
                #out.record()
            
            self._val.value = out.value
            if ro:
                self.removeOverlap()
        
        return self
    
    def understroke(self,
        s=0,
        sw=5,
        outline=False,
        dofill=0,
        miterLimit=None
        ):
        if sw == 0:
            return self
        
        def mod_fn(p):
            if not outline:
                return p.fssw(s, s, sw)
            else:
                if dofill:
                    pf = p.copy()
                p.f(s).outline(sw*2, miterLimit=miterLimit)
                if dofill:
                    p.reverse().record(pf)
                return p

        return self.layerv(mod_fn, 1)