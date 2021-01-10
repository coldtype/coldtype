from coldtype import *
from coldtype.grid import Grid

SRFH = 170
STEM = 125
INSTEM = 100
SRFW = INSTEM+STEM+INSTEM

class Glyph(DATPenSet):
    def __init__(self, frame):
        super().__init__()
        self.addFrame(frame)
        setattr(self, "bx", frame)
        self.registrations = {}
    
    def register(self, fn):
        if callable(fn):
            res = fn(self)
        else:
            res = fn
        for k, v in res.items():
            self.registrations[k] = v
            setattr(self, k, v)
        return self
    
    def realize(self):
        for k, v in self.registrations.items():
            self.append(DATPen().rect(v).tag(k))
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


def _P(r, mod=None):
    return (Glyph(r.tk(-1, 550, 750))
        .register(lambda g: dict(
            base=g.bx.tk(-1, SRFW+10, SRFH),
            cap=g.bx.tkmnx(SRFW-50).tkmxy(SRFH),
            stem=g.bx.tk(-1, STEM).offset(INSTEM, 0)))
        .register(lambda g: dict(
            mid=(g.bx
                .tkmdy(SRFH-30)
                .tkmnx(g.cap.w)
                .tkmxx(0.5)
                .offset(0, -30))))
        .chain(mod)
        .realize()
        .record(lambda g: DATPen()
            .chain(evencurve, 0.75,
                g.cap.pse, g.mid.pne, g.bx.pe.x-g.stem.w-30)
            .chain(evencurve, 0.65,
                g.mid.pse, g.cap.pne, g.bx.pe.x)
            .closePath()
            .tag("curve")))

def _R(r):
    return (_P(r, mod=lambda g:
        g.register(dict(
            base=g.base.subtract(50, "mxx"),
            mid=g.mid.offset(0, 30),
            baser=g.bx.take(200, "mxx").take(SRFH, "mny").offset(20, 0))))
        .record(lambda g: DATPen()
            .line([
                g.mid.pse.offset(-20, 0),
                g.baser.psw,
                g.bx.pse.offset(-50, 0),
                g.mid.pse.offset(STEM-40, 50)])
            .closePath())
        )

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
    glyph = _R(r)

    (glyph
        .round(0)
        .f(None)
        .s(0)
        .sw(2)
        .translate(100, 100))

    return DATPenSet([
        glyph,
        DATPen().rect(glyph.bx).translate(100, 100).f(None).s(hsl(0.9, a=0.3)).sw(5),
        DATPen().rect(glyph.bounds()).f(None).s(hsl(0.7, a=0.3)).sw(5),
        DATPen().gridlines(r, 50, absolute=True),
        (glyph
            .copy()
            .removeOverlap()
            .f(0)
            .color_phototype(r)
            .img_opacity(0.25)
            .img_opacity(1)
        )
        ])
