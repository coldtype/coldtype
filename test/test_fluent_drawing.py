from coldtype import *
from coldtype.grid import Grid


class glyphfn():
    def __init__(self, w):
        self.w = w
        self.r = Rect(w, 750)

    def __call__(self, func):
        self.func = func
        return self


class Constants():
    def __init__(self):
        self.lookup = {}


class Glyph(DATPenSet):
    def __init__(self):
        self.registrations = {}
        self.c = Constants()
        super().__init__()

    def addFrame(self, frame):
        super().addFrame(frame)
        setattr(self, "bx", frame)
        return self
    
    def constants(self, **kwargs):
        res = kwargs
        
        for k, v in res.items():
            if callable(v):
                v = v(self)
            self.c.lookup[k] = v
            setattr(self.c, k, v)
        return self
    
    def varstr(self, v):
        vs = re.sub(r"\$([^\s]+)", lambda m: str(eval("g.c." + m.group(1), {"g":self})), v)
        vs = re.sub(r"\&([^\s]+)", lambda m: str(eval("g." + m.group(1), {"g":self})), vs)
        print(">>>", vs)
        return vs
    
    def remove(self, k):
        del self.registrations[k]
        return self
    
    def register(self, fn=None, rect=True, **kwargs):
        if fn:
            if callable(fn):
                res = fn(self)
            else:
                res = fn
        else:
            res = kwargs
        
        for k, v in res.items():
            if callable(v):
                v = v(self)
            elif isinstance(v, str):
                v = self.bx / self.varstr(v)
            if rect:
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

@glyphfn(630)
def _A(r, g):
    return (g
        .register(
            bl="-$srfw-20 -$srfh",
            br="+$srfw -$srfh",
            cap="=$srfw +$srfh")
        .remove("stem")
        #.remove("cap")
        .realize()
        .record(DATPen()
            .line([
                g.bl.pnw.offset(100, 0),
                g.cap.psw.offset(50, 0),
                g.cap.pse.offset(-50, 0),
                g.br.pne.offset(-70, 0),
                g.br.pnw.offset(70, 0),
                g.cap.ps,
                g.bl.pne.offset(-100, 0)
            ])))

@glyphfn(550)
def _I(r, g):
    return (g
        .register(
            base="-$srfw+50 -$srfh",
            cap="-$srfw+50 +$srfh",
            stem=g.stem.offset(25, 0))
        .realize())

@glyphfn(550)
def _P(r, g, mod=None):
    return (g
        .register(
            base="-$srfw+10 -$srfh",
            cap="-$srfw-70 +$srfh",
            mid=λg: g.bx / g.varstr("-&cap.w =$srfh-50") / "+0.5 1 ^o 0 -30")
        .chain(mod)
        .realize()
        .record(lambda g: DATPen()
            .chain(evencurve, 0.75,
                g.cap.pse, g.mid.pne, g.bx.pe.x-g.stem.w-30)
            .chain(evencurve, 0.65,
                g.mid.pse, g.cap.pne, g.bx.pe.x)
            .closePath()
            .tag("curve")))

@glyphfn(_P.w)
def _R(r, g):
    return (_P.func(r, g, mod=lambda g:
        g.register(
            base=g.base.subtract(50, "mxx"),
            mid=g.mid.offset(0, 30),
            baser="+200 -$srfh ^o 20 0"))
        .record(lambda g: DATPen()
            .line([
                g.mid.pse.offset(-20, 0),
                g.baser.psw,
                g.bx.pse.offset(-50, 0),
                g.mid.pse.offset(g.c.stem-40, 50)])
            .closePath()))

@glyphfn(580)
def _N(r, g):
    return (g
        .constants(
            nst=g.c.stem-30,
            innst=g.c.instem-20,
            base=λg: g.c.innst*2 + g.c.nst)
        .register(
            base="-$base -$srfh",
            capl="-&base.w +$srfh",
            capr="+&base.w +$srfh",
            steml="-$nst 1 ^o $innst 0",
            stemr="+$nst 1 ^o -$innst 0")
        .remove("stem")
        .realize()
        .append(DATPen()
            .line([
                g.steml.pnw.offset(0, 0),
                g.stemr.pse.offset(-(g.c.nst+g.c.innst), 0),
                g.stemr.pse.offset(-10, 0),
                g.capl.pne])
            .closePath()
            .tag("diagonal")))


caps = [_A, _I, _N, _P, _R]

@animation((1000, 1000), timeline=Timeline(len(caps)), rstate=1)
def curves(f, rs):
    r = f.a.r

    cap = caps[f.i]
    g = (Glyph()
        .addFrame(cap.r)
        .constants(
            srfh=180,
            stem=115,
            instem=100,
            srfw=lambda g: g.c.instem+g.c.stem+g.c.instem)
        .register(
            stem="-$stem 1 ^o $instem 0"))
    
    glyph = cap.func(r, g)

    (glyph
        .round(0)
        .f(None)
        .s(0)
        .sw(2)
        .translate(100, 100))
    
    overlay = Overlay.Info in rs.overlays

    return DATPenSet([
        #glyph,
        #DATPen().rect(glyph.bx).translate(100, 100).f(None).s(hsl(0.9, a=0.3)).sw(5),
        #DATPen().rect(glyph.bounds()).f(None).s(hsl(0.7, a=0.3)).sw(5),
        #DATPen().gridlines(r, 50, absolute=True),
        (glyph
            .copy()
            .removeOverlap()
            .f(0)
            .color_phototype(r)
            .img_opacity(0.25 if overlay else 1)
            #.img_opacity(1)
        )
        ])
