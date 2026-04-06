from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen

from coldtype.runon.path import P

try:
    import skia
except ImportError:
    skia = None


class SkiaPathPen(BasePen):
    def __init__(self, dat, h=None):
        super().__init__()
        self.dat = dat
        self.path = skia.Path()
        
        if h is not None:
            tp = TransformPen(self, (1, 0, 0, -1, 0, h))
            if hasattr(dat, "_val"):
                try:
                    dat._val.replay(tp)
                except TypeError:
                    #print("FAIL")
                    #print(dat._val.value)
                    pass
            else:
                dat.replay(tp)
        else:
            for mv, pts in self.dat.value:
                #if mv == "qCurveTo":
                #    self._qCurveToOne()
                getattr(self, mv)(*pts)
    
    def _moveTo(self, p):
        self.path.moveTo(p[0], p[1])

    def _lineTo(self, p):
        self.path.lineTo(p[0], p[1])

    def _curveToOne(self, p1, p2, p3):
        self.path.cubicTo(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])

    def _qCurveToOne(self, p1, p2):
        self.path.quadTo(p1[0], p1[1], p2[0], p2[1])

    def _closePath(self):
        self.path.close()

    def to_drawing(self):
        def unwrap(p):
            return [p.x(), p.y()]
        
        dp = P()
        for mv, pts in self.path:
            if mv == skia.Path.Verb.kMove_Verb:
                dp.moveTo(unwrap(pts[0]))
            elif mv == skia.Path.Verb.kLine_Verb:
                dp.lineTo(*[unwrap(p) for p in pts[1:]])
            elif mv == skia.Path.Verb.kQuad_Verb:
                dp.qCurveTo(*[unwrap(p) for p in pts[1:]])
            elif mv == skia.Path.Verb.kClose_Verb:
                dp.closePath()
            else:
                print(mv)
        return dp