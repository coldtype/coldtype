from coldtype.test import *
from coldtype.grid import Grid

from fontTools.misc.bezierTools import splitLine

a = [(120, 230)]

class glyphfn():
    def __init__(self, w=1000):
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
    
    def setWidth(self, width):
        self.addFrame(Rect(width, self.bx.h))
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
    
    def get(self, k):
        if k in self.registrations:
            return DATPen().rect(self.registrations[k])
        else:
            tagged = self.fft(k)
            if tagged:
                return tagged.copy()
    
    def remove(self, *args):
        for k in args:
            if k in self.registrations:
                del self.registrations[k]
            else:
                tagged = self.fft(k)
                if tagged:
                    super().remove(tagged)
        return self
    
    def register(self, fn=None, **kwargs):
        if fn:
            if callable(fn):
                res = fn(self)
            else:
                res = fn
        else:
            res = kwargs
        
        def keep(k, v):
            if k != "_":
                self.registrations[k] = v
                setattr(self, k, v)
        
        for k, v in res.items():
            if callable(v):
                v = v(self)
            elif isinstance(v, str):
                v = self.bx / self.varstr(v)
            if "ƒ" in k:
                for idx, _k in enumerate(k.split("ƒ")):
                    keep(_k, v[idx])
            else:
                keep(k, v)
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

@glyphfn()
def _A(r, g):
    return (g
        .register(
            blƒgapƒbr="1 -$srfh ^c $srfw-20 $gap $srfw+20 a")
        .record(DATPen()
            .diagonal_upto(g.bl.pn, 78, 80, g.bx.edge("mxy"))
            .tag("diagl"))
        .record(DATPen()
            .diagonal_upto(g.br.pn, 105, 170, g.bx.edge("mxy"))
            .pvl().mod_pt(0, 0, lambda p: p.offset(-20, 0))
            .tag("diagr"))
        .record(DATPen()
            .rect(g.bx / g.varstr("1 =$xbarh ^o 0 -60"))
            .difference(g.copy())
            .explode()[1]
            .tag("xbar"))
        .remove("stem", "gap"))

@glyphfn()
def _I(r, g):
    return (g
        .setWidth(g.c.srfw+50)
        .register(
            base="1 -$srfh",
            cap="1 +$srfh",
            stem="=$stem 1"))

@glyphfn()
def _H(r, g):
    return (g
        .register(
            blƒgapƒbr="1 -$srfh ^c $srfw $gap $srfw a",
            clƒgapƒcr="1 +$srfh ^c $srfw $gap $srfw a",
            steml="-$stem 1 ^m =&bl.ps.x ø",
            stemr="-$stem 1 ^m =&br.ps.x ø",
            xbar="1 =$xbarh ^m -&steml.pc.x ø ^m +&stemr.pc.x ø")
        .remove("stem", "gap"))

@glyphfn(550)
def _K(r, g):
    return (_H.func(r, g)
        .register(
            xbar=g.xbar.offset(0, -110))
        .record(DATPen()
            .lineTo(g.bx.pc.offset(70, 50))
            .lineTo(g.bx.pc.offset(-20, -10))
            .lineTo(g.br.pn.offset(-g.c.stem/2-20, 0))
            .lineTo(g.br.pn.offset(g.c.stem/2+20, 0))
            .closePath())
        .record(DATPen()
            .lineTo(g.xbar.pnw)
            .lineTo(g.xbar.psw)
            .lineTo(g.cr.ps.offset(g.c.stem/2, 0))
            .lineTo(g.cr.ps.offset(-g.c.stem/2-10, 0))
            .closePath())
        .remove("xbar")
        .remove("stemr"))

@glyphfn()
def _E(r, g):
    return (g
        .setWidth(g.c.stem*5)
        .register(
            base="1 -$srfh",
            cap="1 +$srfh",
            eart="+$stem +$earh",
            earb="+$stem -$earh",
            mid="1 =$xbarh ^m -&stem.pc.x ø ^m +&eart.psw.x-30 ø ^l +450 ø"))

@glyphfn()
def _F(r, g):
    return (_E.func(r, g)
        .remove("earb")
        .register(
            base="-$srfw+10 -$srfh"))

@glyphfn(500)
def _L(r, g):
    return (_E.func(r, g)
        .register(cap="-$srfw +$srfh")
        .remove("eart", "mid"))

@glyphfn()
def _T(r, g):
    return (g
        .setWidth(g.c.stem*5)
        .register(
            base="=$srfw -$srfh",
            cap="1 +$srfh",
            earl="-$stem +$earh",
            earr="+$stem +$earh",
            stem="=$stem 1"))

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
    return (_P.func(r, g, ci=50, mod=lambda g:
        g.register(
            base=g.base.subtract(20, "mxx"),
            mid=g.mid.offset(0, 30).inset(10),
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
            stem=g.c.stem-25,
            instem=g.c.instem-20,
            base=λg: g.c.instem*2 + g.c.stem,
            diagw=80,
            shoulderout=30)
        .register(
            _ƒstemlƒgapƒstemr="c $instem $stem a $stem $instem",
            base="-$base -$srfh",
            capl="1 +$srfh ^m +&steml.pc.x ø",
            capr="+$base +$srfh")
        .append(DATPen()
            .diagonal_upto(
                g.stemr.psw,
                g.stemr.ps.cdist(g.steml.pne.offset(g.c.shoulderout, 0))[1],
                g.c.stem+g.c.diagw,
                g.bx.edge("mxy"))
            .intersection(DATPen().rect(g.gap))
            .tag("diagonal"))
        .register(
            base=g.base.setlmxx(DATPen()
                .rect(g.bx / g.varstr("1 -$srfh"))
                .intersection(g.get("diagonal"))
                .bounds().x-g.c.gap),
            capr=g.capr.setlmnx(DATPen()
                .rect(g.bx / g.varstr("1 +$srfh"))
                .intersection(g.get("diagonal"))
                .bounds().mxx+g.c.gap))
        .remove("stem", "gap"))

@glyphfn(700)
def _M(r, g):
    return (_N.func(r, g)
        .remove("diagonal", "base")
        .constants(
            nosein=40)
        .register(
            basel=g.base,
            baser="+&base.w -$srfh",
            capr="+&capl.w +$srfh")
        .append(DATPen()
            .diagonal_upto(
                g.gap.ps.offset(g.c.nosein, 0),
                g.gap.ps.offset(g.c.nosein, 0).cdist(g.steml.pne.offset(g.c.shoulderout, 0))[1],
                g.c.stem+g.c.diagw,
                g.bx.edge("mxy"))
            .intersection(DATPen().rect(g.gap))
            .tag("diagl"))
        .append(DATPen()
            .diagonal_upto(
                g.gap.ps.offset(-g.c.nosein, 0),
                g.gap.ps.offset(-g.c.nosein, 0).cdist(g.stemr.pnw.offset(-g.c.shoulderout, 0))[1],
                g.c.stem+g.c.diagw,
                g.bx.edge("mxy"))
            .intersection(DATPen().rect(g.gap))
            .tag("diagr"))
        .register(
            basel=g.basel.setlmxx(DATPen()
                .rect(g.bx / g.varstr("1 -$srfh"))
                .intersection(g.get("diagl"))
                .bounds().mnx-g.c.gap),
            baser=g.baser.setlmnx(DATPen()
                .rect(g.bx / g.varstr("1 -$srfh"))
                .intersection(g.get("diagr"))
                .bounds().mxx+g.c.gap+0))
        .append(g.get("diagl")
            .difference(g.get("diagr"))
            .explode()[0]
            .record(g.get("diagr")
                .difference(g.get("diagl"))
                .explode()[0])
            .record(g.get("diagl")
                .intersection(g.get("diagr")))
            .removeOverlap()
            .pvl()
            .mod_pt(0, 0, λp: p.offset(0, -40)))
        .remove("diagl", "diagr"))

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
def _Q(r, g):
    return (_O.func(r, g)
        .record(DATPen()
            .rect(g.bx.take(g.c.stem, "mnx")
                .take(g.c.srfh*2, "mny"))
            .rotate(33)
            .translate(g.bounds().w*0.5+50, -50)))

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
            .moveTo(g.hornr.point("C").offset(0, -10)) # HIRESET
            .boxCurveTo(g.bx.pn.offset(-30, g.c.over), # HISTART
                "NE",
                (0.25, 0.75),
                dict(b=λp: p.offset(-50, 0)))
            .boxCurveTo(g.bx.pnw.offset(2, -g.c.earh/2-50), # HISWING
                "NW",
                0.58)
            .boxCurveTo(g.bx.pse.offset(-g.c.stem-30, g.c.srfh+30), # BIGDOWN
                ("SW", "NE"),
                (0.65, 0.35))
            .boxCurveTo(g.bx.ps.offset(45, g.c.srfh-g.c.over*2), # LOSMALL
                "SE",
                0.6)
            .boxCurveTo(g.hornl.pne, # LOLAND
                "SW",
                0.5,
                dict(c=λp: p.offset(35, -20)))
            .lineTo(g.hornl.point("C").offset(0, 20)) # LORESET
            .boxCurveTo(g.bx.ps.offset(40, -g.c.over), # LOSTART
                "SW",
                (0.25, 0.7),
                dict(b=λp: p.offset(40, 0)))
            .boxCurveTo(g.bx.pse.offset(20, g.c.earh/2+45), # LOSWING
                "SE",
                0.6)
            .boxCurveTo(g.bx.pnw.offset(g.c.stem+70, -g.c.srfh-30), # BIGUP
                ("NE", "SW"),
                (0.65, 0.3))
            .boxCurveTo(g.bx.pn.offset(-20, -g.c.srfh+g.c.over*2), # HISMALL
                "NW",
                0.65)
            .boxCurveTo(g.hornr.psw, # HILAND
                "NE",
                0.4,
                dict(c=λp: p.offset(-35, 40)))
            .closePath()
            .pvl()))

@glyphfn(590)
def _U(r, g):
    c = 70
    ocf = 0.75
    icf = 0.85
    return (g
        .register(
            capl="-$srfw +$srfh",
            capr="+$srfw-60 +$srfh",
            steml=λg: g.stem.setmny(g.c.srfh+c),
            stemr=λg: g.stem.inset(10, 0).setmdx(g.capr.point("C").x).setmny(g.c.srfh+c))
        .constants(
            sc=g.steml.pse.interp(0.5, g.stemr.psw).sety(-g.c.over))
        .remove("stem")
        .record(DATPen()
            .moveTo(g.steml.psw)
            .uTurnTo(g.c.sc, g.stemr.pse, ("SW", "SE"), ocf)
            .lineTo(g.stemr.psw)
            .uTurnTo(g.c.sc.offset(0, g.c.srfh), g.steml.pse, ("SE", "SW"), icf)
            .tag("curve")))

@glyphfn(_U.w)
def _V(r, g):
    return (_U.func(r, g)
        .constants(
            sc=g.capl.pc.interp(0.5, g.capr.pc).sety(0))
        .record(DATPen()
            .moveTo(g.capl.pc.offset(-g.c.stem*0.75, 0))
            .lineTo(g.c.sc.offset(-60, 0))
            .lineTo(g.c.sc.offset(g.c.stem-60, 0))
            .lineTo(g.capr.pc.offset(50, 0))
            .lineTo(g.capr.pc.offset(-20, 0))
            .lineTo(g.c.sc.offset(20, g.c.srfh))
            .lineTo(g.capl.pc.offset(g.c.stem/2, 0))
            .closePath())
        .remove("steml")
        .remove("stemr")
        .remove("curve"))

caps = [_A, _B, _C, _D, _E, _F, _G, _H, _I, _K, _L, _M, _N, _O, _P, _Q, _R, _S, _T, _U, _V]

@animation((2000, 1000), timeline=Timeline(len(caps)), rstate=1, storyboard=[0])
def curves(f, rs):
    r = f.a.r

    cap = caps[f.i]
    g = (Glyph()
        .addFrame(cap.r)
        .constants(
            srfh=190,
            stem=105,
            instem=105,
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
        glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.bounds().w+30, 0).f(0).s(None).color_phototype(r, blur=5),
        #show_points(glyph.pen(), Style(recmono, 100))
        ])
