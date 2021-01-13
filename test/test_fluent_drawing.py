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
            elif isinstance(v, str):
                v = self.bx / self.varstr(v)
            self.c.lookup[k] = v
            setattr(self.c, k, v)
        return self
    
    def varstr(self, v):
        vs = re.sub(r"\$([^\s]+)", lambda m: str(eval("g.c." + m.group(1), {"g":self})), v)
        vs = re.sub(r"\&([^\s]+)", lambda m: str(eval("g." + m.group(1), {"g":self})), vs)
        #print(">>>", vs)
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


def evencurve(p:DATPen, t, a, b, x=0):
    if len(p.value) == 0:
        p.moveTo(a)
    else:
        p.lineTo(a)
    
    try:
        t1, t2 = t
    except TypeError:
        t1, t2 = t, t
    
    ex = a.interp(0.5, b).setx(x)
    c1 = a.setx(x)
    c2 = b.setx(x)
    p.curveTo(a.interp(t1, c1), ex.interp(t2, c1), ex)
    p.curveTo(ex.interp(t2, c2), b.interp(t1, c2), b)

def evencurvey(p:DATPen, t, a, b, y):
    if len(p.value) == 0:
        p.moveTo(a)
    else:
        p.lineTo(a)
    
    try:
        t1, t2 = t
    except TypeError:
        t1, t2 = t, t
    
    ey = a.interp(0.5, b).sety(y)
    c1 = a.sety(y)
    c2 = b.sety(y)
    p.curveTo(a.interp(t1, c1), ey.interp(t2, c1), ey)
    p.curveTo(ey.interp(t2, c2), b.interp(t1, c2), b)

@glyphfn(750)
def _A(r, g):
    b = g.bx.take(g.c.srfh, "mny").take(g.c.srfw, "mnx")
    gap, bl = b.divide(g.c.gap, "mxx")
    br = b.offset(gap.pse.x, 0)

    bli = 100
    bri = 80

    return (g
        .register(
            bl=bl,
            br=br,
            cap="=$srfw +$srfh",
            xbar=λg: g.bx.take(g.c.xbarh, "mdy")
                .offset(0, -50)
                .setmnx(g.bl.pne.offset(-bli, 0).x)
                .setmxx(g.br.pnw.offset(bri, 0).x))
        .constants(
            t=g.bl.pne.offset(14, 0).sety(g.bx.h),#.pn.offset(-10, 0),
            tl=λg: g.c.t.offset(-70, 0),
            tr=λg: g.c.t.offset(80, 0))
        .remove("stem")
        .remove("cap")
        .record(DATPen()
            .line([
                g.bl.pnw.offset(bli, 0),
                g.c.tl,
                g.c.tr,
                g.br.pne.offset(-bri, 0),
                g.br.pnw.offset(bri, 0),
                g.c.tr.offset(-130, 0),
                g.c.tl.offset(85, 0),
                g.bl.pne.offset(-bli, 0)
            ]).reverse()))

@glyphfn(550)
def _I(r, g):
    return (g
        .register(
            base="-$srfw+50 -$srfh",
            cap="-$srfw+50 +$srfh",
            stem=g.stem.offset(25, 0)))

@glyphfn(750)
def _H(r, g):
    return (g
        .register(
            bl="-$srfw -$srfh",
            br=λg: g.bl.offset(g.bl.w+g.c.gap, 0),
            cl="-$srfw +$srfh",
            cr=λg: g.cl.offset(g.cl.w+g.c.gap, 0),
            stemr=λg: g.stem.offset(g.cl.w+g.c.gap, 0),
            xbar=λg: g.stem.union(g.stemr).take(g.c.xbarh, "mdy")
        ))

@glyphfn(500)
def _E(r, g):
    return (g
        .register(
            base="1 -$srfh",
            cap="1 +$srfh",
            eart="+$stem +$earh",
            earb="+$stem -$earh",
            mid=λg: g.bx.take(g.c.xbarh, "mdy")
                .subtract(g.c.instem, "mnx")
                .subtract(g.eart.w+30, "mxx")))

@glyphfn(500)
def _F(r, g):
    return (_E.func(r, g)
        .remove("earb")
        .register(
            base="-$srfw+10 -$srfh"))

@glyphfn(550)
def _T(r, g):
    return (g
        .register(
            base="=$srfw -$srfh",
            cap="1 +$srfh",
            earl="-$stem +$earh",
            earr="+$stem +$earh",
            stem=g.bx.take(g.stem.w, "mdx")))

@glyphfn(500)
def _L(r, g):
    return (g
        .register(
            base="1 -$srfh",
            cap="-$srfw +$srfh",
            ear="+$stem -$earh"
        ))

@glyphfn(550)
def _P(r, g, mod=None, xc=0, ci=30):
    return (g
        .register(
            base="-$srfw+10 -$srfh",
            cap="-$srfw-50 +$srfh",
            mid=λg: g.bx / g.varstr("-&cap.w =$srfh-90") / "+0.5 1 ^o 0 -30")
        .chain(mod)
        .record(lambda g: DATPen()
            .chain(evencurve, 0.9,
                g.cap.pse, g.mid.pne, g.bx.pe.x-g.stem.w-ci+xc)
            .chain(evencurve, 0.65,
                g.mid.pse, g.cap.pne, g.bx.pe.x+xc)
            .closePath()
            .tag("curve")))

@glyphfn(_P.w)
def _B(r, g):
    return (_P.func(r, g, xc=-20, ci=20, mod=lambda g:
        g.register(
            base=g.base.take(g.cap.w, "mnx"),
            mid=g.mid.offset(20, 30).inset(5)))
        .record(lambda g: DATPen()
            .chain(evencurve, 0.9,
                g.mid.pse, g.base.pne, g.bx.pe.x-g.stem.w-30)
            .chain(evencurve, 0.7,
                g.base.pse, g.mid.pne.offset(-150, 0), g.bx.pe.x+20)
            .closePath()))

@glyphfn(_P.w)
def _D(r, g):
    g = (_P.func(r, g, xc=30, ci=60, mod=lambda g:
        g.register(mid=g.base.take(g.cap.w, "mnx"))
            .remove("base")))
    (g.fft("curve")
        .pvl()
        .mod_pt(4, -1, λp: p.offset(0, 30))
        .mod_pt(1, -1, λp: p.offset(0, 30)))
    return g

@glyphfn(_P.w)
def _R(r, g):
    return (_P.func(r, g, mod=lambda g:
        g.register(
            base=g.base.subtract(20, "mxx"),
            mid=g.mid.offset(0, 30),
            baser="+$srfw-60 -$srfh ^o 30 0"))
        .record(DATPen()
            .moveTo(g.mid.pse.offset(-50, 0))
            .boxCurveTo(g.baser.pnw, ("NE"), 0.75)
            #.lineTo(g.baser.psw)
            .boxCurveTo(g.baser.ps.offset(20, 0), "SW", 0.75)
            .lineTo(g.baser.pse)
            .lineTo(g.baser.pne)
            .lineTo(g.baser.pne.offset(-g.c.stem, 0))
            .boxCurveTo(g.mid.pse.offset(50, 20), "NE", 0.65)
            .closePath())
        .remove("baser")
        -.record(lambda g: DATPen()
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
        .append(DATPen()
            .line([
                g.steml.pnw.offset(0, 0),
                g.stemr.pse.offset(-(g.c.nst+g.c.innst), 0),
                g.stemr.pse.offset(-10, 0),
                g.capl.pne])
            .closePath()
            .tag("diagonal")))

@glyphfn(500)
def _O(r, g, clx=0):
    (g.constants(
        hw=g.c.stem+20,
        o=g.bx.inset(0, g.c.over),
        oc=λg: g.c.o.inset(g.c.hw, g.c.srfh)))

    outer = (DATPen()
        .tag("O")
        .chain(evencurvey, 0.65,
            g.c.o.pe.offset(0, 50),
            g.c.o.pw.offset(0, 50),
            g.c.o.pn.y,
            )
        .chain(evencurvey, 0.65,
            g.c.o.pw.offset(0, -50),
            g.c.o.pe.offset(0, -50),
            g.c.o.ps.y)
        .closePath())
    
    g.add_data("outer", outer.copy())

    return (g
        .remove("stem")
        .record(outer
            .record(DATPen()
                .chain(evencurvey, 0.85,
                    g.c.oc.pe.offset(0, 40),
                    g.c.oc.pw.offset(0+clx, 40),
                    g.c.oc.pn.y,
                    )
                .chain(evencurvey, 0.85,
                    g.c.oc.pw.offset(0+clx, -40),
                    g.c.oc.pe.offset(0, -40),
                    g.c.oc.ps.y)
                .closePath()
                .reverse())))

@glyphfn(_O.w)
def _C(r, g):
    g = _O.func(r, g, clx=15)
    ht, hm, hb = g.bx.take(g.c.hw, "mxx").divide(g.c.xbarh, "mdy")
    O = g.fft("O")
    O.difference(DATPen().rect(hm))
    O.add_pt(0, 0.5, λp: p.offset(0, -100))
    O.mod_pt(2, -1, λp: p.offset(-10, 0))
    O.mod_pt(2, -2, λp: p.offset(30, 0))
    
    return (g
        .register(
            horn=f"+{ht.w} +{ht.h}"
            ))

@glyphfn(_C.w)
def _G(r, g):
    g = _C.func(r, g)
    xbar = g.bx / g.varstr("+0.5 =$xbarh ^o 0 -50")
    g.record(DATPen().rect(xbar).intersection(g.data["outer"].copy()))
    return g

@glyphfn(500)
def _S(r, g):
    return (g
        .remove("stem")
        .register(
            hornl="-$stem -$earh",
            hornr="+$stem +$earh-10")
        .record(DATPen()
            .moveTo(g.hornr.point("C").offset(0, -10)) # TOPRESET
            .boxCurveTo(g.bx.pn.offset(-30, g.c.over), # TOPBEGIN
                "NE",
                (0.25, 0.75),
                dict(b=λp: p.offset(-50, 0)))
            .boxCurveTo(g.bx.pnw.offset(2, -g.c.earh/2-50), # OUTLEFT
                "NW",
                0.58)
            .boxCurveTo(g.bx.pse.offset(-g.c.stem-30, g.c.srfh+30), # BIGDOWN
                ("SW", "NE"),
                (0.65, 0.35))
            .boxCurveTo(g.bx.ps.offset(35, g.c.srfh-g.c.over*2), # BOTSMALL
                "SE",
                0.6)
            .boxCurveTo(g.hornl.pne, # BOTLAND
                "SW",
                0.5,
                dict(c=λp: p.offset(35, -20)))
            .lineTo(g.hornl.point("C").offset(0, 20)) # BOTRESET
            .boxCurveTo(g.bx.ps.offset(40, -g.c.over), # BOTBEGIN
                "SW",
                (0.25, 0.7),
                dict(b=λp: p.offset(40, 0)))
            .boxCurveTo(g.bx.pse.offset(20, g.c.earh/2+45), # OUTRIGHT
                "SE",
                0.6)
            .boxCurveTo(g.bx.pnw.offset(g.c.stem+50, -g.c.srfh-30), # BIGUP
                ("NE", "SW"),
                (0.65, 0.35))
            .boxCurveTo(g.bx.pn.offset(-20, -g.c.srfh+g.c.over*2), # TOPSMALL
                "NW",
                0.65)
            .boxCurveTo(g.hornr.psw, # TOPLAND
                "NE",
                0.4,
                dict(c=λp: p.offset(-35, 40)))
            .closePath()
            .pvl()))

caps = [_A, _B, _C, _D, _E, _F, _G, _H, _I, _L, _N, _O, _P, _R, _S, _T]

@animation((1300, 1000), timeline=Timeline(len(caps)), rstate=1, storyboard=[2])
def curves(f, rs):
    r = f.a.r

    cap = caps[f.i]
    g = (Glyph()
        .addFrame(cap.r)
        .constants(
            srfh=190,
            stem=115,
            instem=100,
            xbarh=100,
            over=10,
            gap=20,
            earh=λg: g.bx.divide(g.c.xbarh, "mdy")[0].h,#.srfh + 150,
            srfw=λg: g.c.instem + g.c.stem + g.c.instem)
        .register(
            stem="-$stem 1 ^o $instem 0"))

    glyph = (cap.func(r, g)
        .realize()
        .round(0)
        .f(None)
        .s(0)
        .sw(2)
        .translate(100, 100))
    
    overlay = Overlay.Info in rs.overlays

    return DATPenSet([
        glyph.copy().f(None).s(0, 0.5).sw(10),
        DATPen().rect(glyph.bx).translate(100, 100).f(None).s(hsl(0.9, a=0.3)).sw(5) if overlay else None,
        DATPen().rect(glyph.bounds()).f(None).s(hsl(0.7, a=0.3)).sw(5) if overlay else None,
        DATPen().gridlines(r, 50, absolute=True) if overlay else None,
        #(glyph
        #    .copy()
        #    .pen()
        #    .removeOverlap()
        #    .f(0)
        #    .color_phototype(r)
        #    .img_opacity(0.25 if overlay else 1)
        #    #.img_opacity(1)
        #),
        (glyph.pen().skeleton()) if overlay else None,
        glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.bounds().w+30, 0).f(0).s(None).color_phototype(r, blur=5)
        ])
