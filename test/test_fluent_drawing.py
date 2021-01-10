from coldtype import *
from coldtype.grid import Grid

SRFH = 170
STEM = 125
INSTEM = 100
SRFW = INSTEM+STEM+INSTEM

class Glyph(DATPen):
    def __init__(self, frame):
        super().__init__()
        self.addFrame(frame)
        setattr(self, "bx", frame)
    
    def register(self, fn):
        res = fn(self, self.frame)
        for k, v in res.items():
            setattr(self, k, v)
            self.rect(v)
        return self
    
    def record(self, fn):
        if callable(fn):
            return super().record(fn(self))
        else:
            return super().record(fn)


def evencurve(p:DATPen, t, a, b, x):
    if len(p.value) == 0:
        p.moveTo(a)
    else:
        p.lineTo(a)
    
    ex = a.interp(0.5, b).setx(x)
    c1 = a.setx(x)
    c2 = b.setx(x)
    p.curveTo(a.interp(t, c1), ex.interp(t, c1), ex)
    p.curveTo(ex.interp(t, c2), b.interp(t, c2), b)


def _P(r, mdo=-30):
    return (Glyph(r.tk(-1, 550, 750))
        .register(lambda g, bx: dict(
            base=bx.tk(-1, SRFW+10, SRFH),
            cap=bx.tkmnx(SRFW-50).tkmxy(SRFH),
            stem=bx.tk(-1, STEM).offset(INSTEM, 0)))
        .register(lambda g, bx: dict(
            mid=(bx
                .tkmdy(SRFH-30)
                .tkmnx(g.cap.w)
                .tkmxx(0.5)
                .offset(0, mdo))))
        .record(lambda g: DATPen()
            .chain(evencurve, 0.75, g.cap.pse, g.mid.pne, g.bx.pe.x-g.stem.w-20)
            .chain(evencurve, 0.65, g.mid.pse, g.cap.pne, g.bx.pe.x)
            .closePath()))

def _R(r):
    bx, glyph = _P(r, mdo=20)
    return bx, (glyph
        .record(DATPen()
            ))

def _N(r):
    stem = STEM-30
    instem = INSTEM-20
    bx = r.tkmny(750).tkmnx(650)
    base = bx.tkmny(SRFH).tkmnx(instem*2+stem)
    capl = bx.tkmxy(SRFH).tkmnx(base.w)
    capr = bx.tkmxy(SRFH).tkmxx(0.45)
    steml = bx.tkmnx(stem).offset(instem, 0)
    stemr = bx.tkmxx(stem).offset(-instem, 0)
    return bx, (DATPen()
        .rect(base)
        .rect(capl)
        .rect(capr)
        .rect(steml)
        .rect(stemr)
        .line([
            steml.pnw.offset(0, 0),
            stemr.pse.offset(-(stem+instem), 0),
            stemr.pse.offset(-10, 0),
            capl.pne]).closePath())


@renderable((1000, 1000))
def curves(r):
    glyph = _P(r)

    (glyph
        .round(0)
        .f(None)
        .s(0)
        .sw(2)
        .translate(100, 100))

    return DATPenSet([
        glyph,
        DATPen().rect(glyph.bx).translate(100, 100).f(None).s(hsl(0.9, a=0.3)).sw(5),
        DATPen().gridlines(r, 50, absolute=True),
        glyph.copy().removeOverlap().f(0).color_phototype(r).img_opacity(0.25)
        ])
