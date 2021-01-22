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


class Glyph(DATPens):
    def addFrame(self, frame):
        super().addFrame(frame)
        setattr(self, "bx", frame)
        return self
    
    def setWidth(self, width):
        self.addFrame(Rect(width, self.bx.h))
        return self
    
    @property
    def bxr(self):
        return DATPen().rect(self.bx)

@glyphfn()
def _A(r, g):
    return (g
        .register(
            blƒgapƒbr="1 -$srfh ^c $srfw-20 $gap $srfw+20 a")
        .constants(
            hdiag_line=Line(g.br.pn, y:=g.bx.pn.setx(g.br.pnw.x) / 0),
            ldiag_line=λg: Line(g.bl.pn, y / (-g.c.hdiag*0.16)))
        .append(DATPen()
            .line(g.c.hdiag_line)
            .outline(g.c.hdiag)
            .tag("diagr")
            .intersection(DATPen()
                .fence(g.c.ldiag_line, ~g.bx.edge("mxx"))))
        .append(DATPen()
            .line(g.c.ldiag_line)
            .outline(g.c.ldiag)
            .intersection(g.bxr)
            .tag("diagl"))
        .append(~DATPen()
            .line(Line(
                g.c.hdiag_line.t(t:=0.21),
                g.c.ldiag_line.t(t))
                .extr(-0.15))
            .outline(g.c.xbarh))
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
def _J(r, g):
    c = 90
    return (g
        .setWidth(g.c.stem*4.25)
        .register(
            stem=f"+$stem 1 ^o -$instem 0 ^s 0 -$srfh+{c}",
            ear=f"-$stem+20 -$earh+30 ^s 0 -$srfh+{c}",
            cap="+$srfw +$srfh")
        .append(DATPen()
            .moveTo(a:=g.stem.psw // 60)
            .boxCurveTo(i:=a.i(0.5, g.ear.pne) @ g.c.srfh, "SE", c:=0.77)
            .boxCurveTo(g.ear.pne, "SW", c+0.03)
            .lineTo(g.ear.pnw)
            .boxCurveTo(i @ 0 / 0, "SW", c:=0.77)
            .boxCurveTo(g.stem.pse, "SE", c-0.08)
            .closePath()
            .pvl()
            -.mod_pt(5, 1, λp: p / -1))
        .remove("ear"))

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
    cmp = 20
    return (_H.func(r, g)
        .constants(
            udiag=Line(g.stem.pc // -100, g.cr.ps).extr(0.1),
            inr=Rect.FromPoints(g.stem.psw, g.cr.pne))
        .append(DATPen()
            .line(g.c.udiag)
            .outline(g.c.ldiag+cmp)
            .reverse()
            .intersection(DATPen().rect(g.c.inr)))
        .append(DATPen()
            .line(Line(g.br.pn, g.cl.ps / 70).extr(0.5))
            .outline(g.c.hdiag-cmp)
            .intersection(
                DATPen().fence(g.c.udiag, [g.cr.pne, g.br.pse])))
        .remove("xbar", "stemr"))

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

@glyphfn()
def _L(r, g):
    return (g
        .setWidth(g.c.stem*4.25)
        .register(
            base="1 -$srfh",
            cap="-$srfw +$srfh",
            earb="+$stem -$earh"))

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

@glyphfn(570)
def _P(r, g, mod=None, xc=0, ci=30):
    return (g
        .register(
            base="-$srfw+10 -$srfh",
            cap="-$srfw-50 +$srfh",
            mid=λg: g.bx / g.varstr("-&cap.w =$srfh-90") / "+0.5 1 ^o 0 -30")
        .chain(mod)
        .record(lambda g: DATPen()
            .moveTo(g.cap.pse)
            .uTurnTo(g.cap.pse.i(0.5, g.mid.pne).setx(g.bx.mxx-g.stem.w-ci+xc),
                g.mid.pne, ("NE", "SE"), 0.9)
            .lineTo(g.mid.pse)
            .uTurnTo(g.mid.pse.i(g.cap.pne).setx(g.bx.pe.x+xc),
                g.cap.pne, ("SE", "NE"), 0.65)
            .closePath()
            .tag("curve")))

@glyphfn(_P.w)
def _B(r, g):
    return (_P.func(r, g, xc=-20, ci=20, mod=lambda g:
        g.register(
            base=g.base.take(g.cap.w, "mnx"),
            mid=g.mid.offset(20, 30).inset(5)))
        .record(lambda g: DATPen()
            .moveTo(g.mid.pse)
            .uTurnTo(g.mid.pse.i(g.base.pne).setx(g.bx.pe.x-g.stem.w-30),
                g.base.pne, ("NE", "SE"), 0.9)
            .lineTo(g.base.pse)
            .uTurnTo(g.base.pse.i(g.mid.pne).setx(g.bx.pe.x+20),
                g.mid.pne.offset(-150, 0), ("SE", "NE"), 0.7)
            .closePath()))

@glyphfn(_P.w)
def _D(r, g):
    g = (_P.func(r, g, xc=30, ci=60, mod=lambda g:
        g.register(mid=g.base.take(g.cap.w, "mnx"))
            .remove("base")))
    (g.fft("curve")
        .pvl()
        .mod_pt(4, -1, λp: p.offset(0, 40))
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
            .boxCurveTo(g.baser.ps.offset(20, 0), "SW", 0.75)
            .lineTo(g.baser.pse)
            .lineTo(g.baser.pne)
            .lineTo(g.baser.pne.offset(-g.c.stem, 0))
            .boxCurveTo(g.mid.pse.offset(50, 20), "NE", 0.65)
            .translate(10, 0)
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
            diagw=90,
            shoulderout=30)
        .register(
            _ƒstemlƒgapƒstemr="c $instem $stem a $stem $instem",
            base="-$base -$srfh",
            capl="1 +$srfh ^m +&steml.pc.x ø",
            capr="+$base +$srfh")
        .append(DATPen()
            .diagonal_upto(
                g.stemr.psw,
                g.stemr.ps.cdist(g.steml.pne / g.c.shoulderout)[1],
                g.c.stem + g.c.diagw,
                g.bx.edge("mxy"))
            .intersection(DATPen().rect(g.gap))
            .tag("diagonal"))
        .register(
            base=g.base.setlmxx(DATPen()
                .rect(g.bx / g.varstr("1 -$srfh"))
                .intersection(g.get("diagonal"))
                .bounds().x - g.c.gap),
            capr=g.capr.setlmnx(DATPen()
                .rect(g.bx / g.varstr("1 +$srfh"))
                .intersection(g.get("diagonal"))
                .bounds().mxx + g.c.gap))
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
            .mod_pt(0, 0, λp: p.offset(0, -70))
            )
        .remove("diagl", "diagr"))

@glyphfn(500)
def _O(r, g, clx=0):
    (g.constants(
        hw=g.c.stem+10,
        o=g.bx.inset(0, -g.c.over),
        i=λg: g.c.o.inset(g.c.hw, g.c.srfh)))

    def o(r, off, offc):
        return (DATPen()
            .moveTo(r.pe.offset(0, off))
            .uTurnTo(r.pn, r.pw.offset(0, off),
                ("NE", "NW"), offc)
            .lineTo(r.pw.offset(0, -off))
            .uTurnTo(r.ps, r.pe.offset(0, -off),
                ("SW", "SE"), offc)
            .closePath())
    
    outer = o(g.c.o, 40, 0.65).tag("O")
    inner = o(g.c.i.subtract(clx, "mnx"), 16, 0.85).tag("O_counter").reverse()
    
    g.add_data("outer", outer.copy())

    return (g
        .remove("stem")
        .record(outer.record(inner)))

@glyphfn(_O.w)
def _Q(r, g):
    return (_O.func(r, g)
        .record(DATPen()
            .rect(g.bx.take(g.c.stem, "mnx")
                .take(g.c.srfh*2, "mny"))
            .rotate(33)
            .translate(g.bounds().w*0.5+50, -50)))

def _CG(r, g):
    g = _O.func(r, g, clx=15)
    ht, hm, hb = g.bx.take(g.c.hw, "mxx").divide(g.c.xbarh, "mdy")
    
    return (g
        .register(horn=f"+{ht.w} +{ht.h}")
        .fft("O", λp: (p
            .add_pt(0, 0.5, λp: p.offset(0, -100))
            .mod_pt(2, -1, λp: p.offset(-10, 0))
            .mod_pt(2, -2, λp: p.offset(30, 0))
            .difference(DATPen().rect(hm.add(10, "mnx")))
            .pvl())))

@glyphfn(_O.w)
def _C(r, g):
    return (_CG(r, g)
        .fft("O", λp: (p
            .mod_pt(6, 0, λp: p.offset(5, 0))
            .mod_pt(7, 0, λp: p.offset(-10, 0))
            .mod_pt(5, 2, λp: p.offset(5, 0)))))

@glyphfn(_C.w)
def _G(r, g):
    g = (_CG(r, g)
        .append(
            DATPen()
            .rect(g.bx / g.varstr("+0.5 =$xbarh ^o 0 -50"))
            .pvl()
            .mod_pt(1, 0, λp: p.offset(-20, 0))
            .tag("xbar"))
        .fft("O", λp: (p
            .mod_pt(5, 0, λp: p.offset(25, 0))
            .mod_pt(5, 2, λp: p.offset(0, 50)))))
    #xbar = g.bx / g.varstr()
    #g.record(DATPen().rect(xbar).intersection(g.data["outer"].copy()))
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
            .boxCurveTo(g.bx.ps.offset(35, g.c.srfh-g.c.over*2), # LOSMALL
                "SE",
                0.63)
            .boxCurveTo(g.hornl.pne, # LOLAND
                "SW",
                (0.35, 0.84),
                dict(c=λp: p.offset(45, 0)))
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
                (0.65, 0.37))
            .boxCurveTo(g.bx.pn.offset(-10, -g.c.srfh+g.c.over*2), # HISMALL
                "NW",
                0.65)
            .boxCurveTo(g.hornr.psw, # HILAND
                "NE",
                0.4,
                dict(c=λp: p.offset(-25, 40)))
            .closePath()
            .pvl()))

@glyphfn()
def _U(r, g):
    c = 90
    return (g
        .register(
            caplƒ_ƒcapr="1 +$srfh ^c $srfw+20 $gap $srfw-60 a",
            steml=λg: g.stem.setmny(g.c.srfh+c),
            stemr=λg: g.stem / g.varstr(f"=$ldiag+10 1 ^m =&capr.pc.x -$srfh+{c}"))
        .constants(
            sc=g.steml.pse.interp(0.5, g.stemr.psw).sety(-g.c.over))
        .remove("stem")
        .record(DATPen()
            .moveTo(g.steml.psw)
            .uTurnTo(g.c.sc, g.stemr.pse, ("SW", "SE"), 0.75)
            .lineTo(g.stemr.psw)
            .uTurnTo(g.c.sc.offset(0, g.c.srfh), g.steml.pse, ("SE", "SW"), 0.85)
            .closePath()
            .tag("curve")))

@glyphfn(_U.w)
def _V(r, g):
    return (_U.func(r, g)
        .constants(
            hdiag_line=Line(g.capl.ps, y:=g.bx.ps.setx(g.capl.mxx)),
            ldiag_line=Line(g.capr.ps, y / (-g.c.hdiag*0.16)))
        .append(DATPen()
            .line(g.c.hdiag_line)
            .outline(g.c.hdiag)
            .intersection(DATPen()
                .fence(g.c.ldiag_line, g.bx.edge("mnx"))))
        .append(DATPen()
            .line(g.c.ldiag_line)
            .outline(g.c.ldiag)
            .intersection(g.bxr))
        .remove("steml", "stemr", "curve"))

@glyphfn()
def _W(r, g):
    return (g
        .constants(srfw=g.c.srfw-50)
        .register(
            caplƒ_ƒcapmƒ_ƒcapr="1 +$srfh ^c $srfw $gap $srfw-10 $gap $srfw-20 a")
        .constants(
            hdiag=g.c.hdiag-20,
            ldiag=g.c.ldiag+15,
            hd1=Line(g.capl.ps, p1:=g.capl.pse.sety(0)),
            hd2=Line(p2:=g.capm.ps / 5, p3:=g.capm.pse.sety(0)),
            ld1=Line(p1 / (nudge:=10), p2 / -25),
            ld2=Line(p3 / (nudge), g.capr.ps))
        .append(DATPen()
            .line(g.c.hd1)
            .outline(g.c.hdiag)
            .intersection(DATPen().fence(g.bx.edge("mnx"), ~g.c.ld1)))
        .append(DATPen()
            .line(g.c.hd2)
            .outline(g.c.hdiag)
            .intersection(DATPen().fence(g.bx.edge("mnx"), ~g.c.ld2)))
        .append(DATPen()
            .line(g.c.ld1)
            .outline(g.c.ldiag)
            .intersection(g.bxr))
        .append(DATPen()
            .line(g.c.ld2)
            .outline(g.c.ldiag)
            .intersection(g.bxr))
        .remove("stem"))

@glyphfn()
def _X(r, g):
    f = 50
    skew = 0.04
    return (g
        .register(
            blƒbgapƒbr=f"1 -$srfh ^c $srfw-{f} $gap $srfw+{f} a",
            clƒcgapƒcr=f"1 +$srfh ^c $srfw+{f} $gap $srfw-{f} a")
        .constants(
            hdiag_line=Line(g.cl.ps, g.br.pn))
        .append(~DATPen()
            .line(g.c.hdiag_line)
            .outline(g.c.hdiag))
        .append(DATPen()
            .line(Line(g.bl.pn, g.c.hdiag_line.t(0.5-skew)).extr(0.3))
            .outline(g.c.ldiag)
            .intersection(DATPen()
                .fence(g.bx.edge("mnx"), g.c.hdiag_line)))
        .append(DATPen()
            .line(Line(g.cr.ps, g.c.hdiag_line.t(0.5+skew)).extr(0.3))
            .outline(g.c.ldiag)
            .intersection(DATPen()
                .fence(g.bx.edge("mxx"), g.c.hdiag_line)))
        .remove("cgap", "bgap", "stem"))

@glyphfn()
def _Y(r, g):
    f = 50
    yup = 120
    return (g
        .register(
            clƒgapƒcr=f"1 +$srfh ^c $srfw+{f} $gap $srfw-{f} a",
            base="1 -$srfh ^m -&cl.pc.x-10 ø ^m +&cr.pc.x+10 ø",
            stem=λg: g.stem / g.varstr("=$hdiag -0.5 ^m =&base.pc.x ø"))
        .append(DATPen()
            .line(Line(g.cl.ps, g.base.pn // yup))
            .outline(g.c.hdiag)
            .intersection(DATPen()
                .rect(g.bx.setmxx(g.stem.mxx))))
        .append(~DATPen()
            .line(Line(g.cr.ps, g.base.pn // (yup-30)))
            .outline(g.c.ldiag))
        .remove("gap"))

@glyphfn()
def _Z(r, g:Glyph):
    diag = g.c.ldiag + 50
    return (g
        .setWidth(g.c.stem*4.5)
        .register(
            cap="1 +$srfh",
            base="1 -$srfh",
            eart="-$stem +$earh",
            earb="+$stem -$earh")
        .append(DATPen()
            .line(l:=Line(g.cap.pne // (d:=diag-20), g.base.psw // -d))
            .outline(diag)
            .intersection(g.bxr))
        .append(DATPen()
            .rect(g.cap)
            .intersection(DATPen()
                .fence(g.bx.edge("mnx"), g.bx.edge("mxy"), l)))
        .append(DATPen()
            .rect(g.base)
            .intersection(DATPen()
                .fence(g.bx.edge("mxx"), ~g.bx.edge("mny"), ~l)))
        .remove("stem", "cap", "base"))

caps = [_A, _B, _C, _D, _E, _F, _G, _H, _I, _J, _K, _L, _M, _N, _O, _P, _Q, _R, _S, _T, _U, _V, _W, _X, _Y, _Z]

@animation((2000, 1000), timeline=Timeline(len(caps)), rstate=1, storyboard=[0])
def curves(f, rs):
    r = f.a.r

    cap = caps[f.i]
    g = (Glyph()
        .addFrame(cap.r)
        .constants(
            srfh=190,
            stem=115,
            instem=105,
            xbarh=100,
            over=10,
            gap=20,
            hdiag=λ.c.stem+50,
            ldiag=λ.c.stem-50,
            earh=λ.bx.divide(x.c.xbarh, "mdy")[0].h,
            srfw=λ.c.instem + x.c.stem + x.c.instem)
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

    lpts = DATPens()
    txtstyle = Style("Times", 24, load_font=0, fill=hsl(0.4, 1))

    for p in glyph:
        for idx, (mv, pts) in enumerate(p.value):
            if len(pts) > 0:
                for jdx, pt in enumerate(pts):
                    lpts += DATText(f"{idx},{jdx}", txtstyle, Rect.FromCenter(pt, 20))

    return DATPenSet([
        glyph.copy().f(None).s(0, 0.5).sw(10) if overlay else None,
        glyph.pen().removeOverlap().f(None).s(0, 1).sw(5) if not overlay else None,
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
        (glyph.pen().skeleton(scale=4).f(None).s(hsl(0.57, 1, 0.47))) if overlay else None,
        glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.bounds().w+30, 0).f(0).s(None).color_phototype(r, blur=5),
        glyph.pen().removeOverlap().scale(0.5, center=Point([100, 100])).translate(glyph.bounds().w+30+glyph.bounds().w*0.75+30, 0).f(None).s(0).sw(3),
        lpts if overlay else None
        #show_points(glyph.pen(), Style(recmono, 100))
        ])
