import math

from fontTools.pens.recordingPen import RecordingPen

from coldtype.pens.outlinepen import OutlinePen
from coldtype.pens.translationpen import TranslationPen, polarCoord


class FXMixin():
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