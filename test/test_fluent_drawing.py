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
    
    def set_width(self, width):
        self.addFrame(Rect(math.floor(width), self.bx.h))
        return self
    
    setWidth = set_width
    
    def add_stem(self):
        return self.register(stem="-$stem 1 ^o $instem 0")
    
    @property
    def bxr(self):
        return DATPen().rect(self.bx)

@glyphfn()
def _A(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{(c:=20)} $gap $srfw+{c} a")
        .declare(
            hd:=Line(g.br.pn, y:=g.bx.pn.setx(g.br.pnw.x) / 0),
            ld:=Line(g.bl.pn, y / (-g.c.hdiag*0.16)))
        .ap(DP("diagr", hd).ol(g.c.hdiag).ƒ(ld, ~g.bx.edge("mxx")))
        .ap(DP("diagl", ld).ol(g.c.ldiag).ƒ(g.bx))
        .ap(DP("xbar", Line(hd.t(t:=0.21), ld.t(t)))
            .ol(g.c.xbarh).ƒ(hd, ~ld)))

@glyphfn()
def _I(r, g):
    return (g
        .set_width(g.c.srfw+50)
        .register(
            base="1 -$srfh",
            cap="1 +$srfh",
            stem="=$stem 1"))

@glyphfn()
def _J(r, g):
    return (g
        .setWidth(g.c.stem*4.25)
        .declare(c:=100)
        .register(
            stem=f"+$stem 1 ^o -$instem 0 ^s 0 -$srfh+{c}",
            ear=f"-$stem+20 -$earh+30 ^s 0 -$srfh+{c}",
            cap="+$srfw +$srfh")
        .ap(DP()
            .mt(a:=g.stem.psw // 60)
            .bct(i:=a.i(0.5, g.ear.pne) @ g.c.srfh, "SE", c:=0.77)
            .bct(g.ear.pne, "SW", c+0.03)
            .lt(g.ear.pnw)
            .bct(i @ 0 / 0, "SW", c:=0.77)
            .bct(g.stem.pse, "SE", c-0.08)
            .cp()
            .pvl())
        .remove("ear"))

@glyphfn()
def _H(r, g, rn=0):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{rn} $gap $srfw+{rn} a",
            clƒ_ƒcr=f"1 +$srfh ^c $srfw-{rn} $gap $srfw+{rn} a",
            steml="-$stem 1 ^m =&bl.ps.x ø",
            stemr="-$stem 1 ^m =&br.ps.x ø",
            xbar="1 =$xbarh ^m -&steml.pc.x ø ^m +&stemr.pc.x ø"))

@glyphfn()
def _K(r, g):
    return (_H.func(r, g, rn=10)
        .ap(DP(
            udiag:=Line(g.steml.pc//-100, g.cr.ps).extr(0.1))
            .ol(g.c.ldiag+(cmp:=20)).ƒ(g.steml.ew, ~g.bx.ee))
        .append(DP(
            Line(g.br.pn, g.cl.ps / 70).extr(0.12))
            .ol(g.c.hdiag-cmp).ƒ(udiag, [g.cr.pne, g.br.pse]))
        .remove("xbar", "stemr"))

@glyphfn()
def _E(r, g):
    return (g
        .setWidth(g.c.stem*4.5)
        .add_stem()
        .register(
            baseƒ_ƒ_cap="r $srfh a $srfh",
            earbƒ_ƒeart="+$stem 1 ^r $earh a $earh",
            mid="1 =$xbarh ^m -&stem.pc.x ø ^m +&eart.psw.x-30 ø ^l +450 ø"))

@glyphfn()
def _F(r, g):
    return (_E.func(r, g)
        .remove("earb")
        .register(base="-$srfw+10 -$srfh"))

@glyphfn()
def _L(r, g):
    return (g
        .set_width(g.c.stem*4.25)
        .add_stem()
        .register(
            base="1 -$srfh",
            cap="-$srfw +$srfh",
            earb="+$stem -$earh"))

@glyphfn()
def _T(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            base="=$srfw -$srfh",
            cap="1 +$srfh",
            earl="-$stem +$earh",
            earr="+$stem +$earh",
            stem="=$stem 1"))

@glyphfn()
def _P(r, g, mod=None, tc=0.6, xc=0, ci=30, my=0):
    return (g
        .set_width(g.c.stem*4.5+xc)
        .add_stem()
        .guide(
            bxc=f"1 +{tc}",
            curve="&bxc ^m -&stem.mxx+50 ø",
            midƒknockƒcap=f"&bxc ^r $xbarh+{my} a $srfh",
            knock=f"&knock ^s +$stem+{ci} 0",
            mid="&mid ^m -&stem.pc.x ø ^m +&curve.mnx ø",
            cap="&cap ^m +&curve.mnx ø")
        .register(
            base="-$srfw+10 -$srfh")
        .chain(mod)
        .constants(cicf=0.9, cocf=0.65)
        .ap(DP("curve")
            .mt(g.cap.pnw)
            .lt(g.cap.psw, g.cap.pse)
            .bct(g.knock.pe, "NE", g.c.cicf)
            .bct(g.mid.pne, "SE", g.c.cicf)
            .lt(g.mid.pnw, g.mid.psw, g.mid.pse)
            .bct(g.curve.pe, "SE", g.c.cocf)
            .bct(g.cap.pne, "NE", g.c.cocf)
            .cp()))

@glyphfn(_P.w)
def _B(r, g):
    return (_P.func(r, g, tc=0.56, my=-5, xc=-20, ci=20, mod=λg: g
        .register(
            base=g.base.take(g.cap.w, "mnx")))
        .guide(
            bbxc=f"1 1 ^m -&curve.mnx +&knock.mny ^e +{(bnx:=20)} 0",
            bknock=f"&bbxc ^m +&knock.mxx+{bnx*0.5} -&base.mxy ^m ø +&mid.mny")
        .ap(DP("belly")
            .declare(
                n:=18,
                cif:=g.c.cicf-0.02,
                cof:=g.c.cocf+0.02)
            .mt(lp:=g.mid.pse)
            .bct(g.bknock.pe, "NE", cif)
            .bct(g.bknock.psw, "SE", cif)
            .lt(g.base.pnw, g.base.psw, g.base.pse)
            .bct(g.bbxc.pe, "SE", cof)
            .bct(g.mid.pne, "NE", cof)
            .cp()
            .declare(c:=20)
            .mod_pt(5, 0, λ/(c:=20))
            .mod_pt(6, 0, λ/(c/2))
            .closePath())
        .remove("base"))

@glyphfn(_P.w)
def _D(r, g):
    g = (_P.func(r, g, tc=1, xc=30, ci=50, mod=λg: g
        .register(mid=g.base.take(g.cap.w, "mnx")))
        .remove("base")
        .fft("curve", λc: c.pvl()
            .declare(q:=30)
            .mod_pt(8, 2, λ//q)
            .mod_pt(3, 2, λ//(q+10))))
    return g

@glyphfn(_P.w)
def _R(r, g):
    return (_P.func(r, g, tc=0.60, xc=20, ci=60, mod=λg: g
        .register(
            base=g.base.subtract(20, "mxx"),
            mid=g.mid.offset(0, 20).inset(10))
        .guide(
            baser="+$srfw-100 -$srfh ^o 30 0")
        .ap(DP("leg")
            .mt(g.mid.pse/-20)
            .bct(g.baser.pnw, "NE", 0.65)
            .bct(g.baser.ps/20, "SW", 0.85)
            .lt(g.baser.pse)
            .lt(p:=g.baser.pne)
            .lt(p/-70)
            .bct(g.mid.pse.o(50, 10), "NE", 0.65)
            .cp())))

@glyphfn()
def _N(r, g):
    return (g
        .set_width(int(g.c.stem*5.25))
        .register(
            _ƒstemlƒ_ƒstemr="c $ninstem $nstem a $nstem $ninstem",
            base="-0.5 -$srfh",
            caplƒ_ƒcapr="1 +$srfh ^c &steml.pc.x a 0.5")
        .ap(diag:=DP("diagonal",
            Line(g.stemr.psw, g.steml.pne / g.c.nshoulder))
            .ol(g.c.hdiag).ƒ(g.steml.ecx, ~g.stemr.ecx))
        .register(
            base=g.base.setlmxx((diag.sl(0) & g.base.en).x - g.c.gap),
            capr=g.capr.setlmnx((diag.sl(3) & g.capr.es).x + g.c.gap+5)))

@glyphfn()
def _M(r, g):
    return (g
        .set_width(g.c.stem*6.60)
        .declare(
            spread:=-60,
            nosein:=30,
            wght:=g.c.hdiag-30)
        .register(
            _ƒstemlƒ_ƒstemr="c $ninstem $nstem a $nstem $ninstem",
            baselƒ_ƒbaser="1 -$srfh ^c $nbase a $nbase",
            caplƒ_ƒcapr=f"1 +$srfh ^c $nbase+{spread} a $nbase+{spread}")
        .append(diagl:=DP("dgl",
            Line(g.capl.pne, g.bx.ps / nosein))
            .ol(wght).ƒ(g.bx))
        .append(diagr:=DP("dgr",
            Line(g.capr.pnw, g.bx.ps / -nosein))
            .ol(wght).ƒ(g.bx))
        .fft("dgl", λ.ƒ(diagr.sl(0), ~g.bx.edge("mnx")))
        .fft("dgr", λ.ƒ(diagl.sl(2), g.bx.edge("mxx"))))

@glyphfn(500)
def _O(r, g, clx=0):
    (g.constants(
        hw=g.c.stem+10,
        o=g.bx.inset(0, -g.c.over),
        i=λ.c.o.inset(g.c.hw, g.c.srfh).subtract(clx, "mnx")))

    def o(r, off, offc):
        return (DATPen()
            .mt(r.pe.offset(0, off))
            .bct(r.pn, "NE", offc)
            .bct(r.pw // off, "NW", offc)
            .lt(r.pw // -off)
            .bct(r.ps, "SW", offc)
            .bct(r.pe // -off, "SE", offc)
            .cp())
    
    return (g
        .ap(o(g.c.o, 40, 0.65).tag("O"))
        .ap(~o(g.c.i, 16, 0.85).tag("Oi")))

@glyphfn(_O.w)
def _Q(r, g):
    return (_O.func(r, g)
        .record(DATPen()
            .rect(g.bx % g.vs("=$stem -$srfh*2 ^o $srfh/2 -$srfh/2-20"))
            .rotate(33)))

def _CG(r, g):
    return (_O.func(r, g, clx=15)
        .register(beardƒapertureƒhorn=f"+$hw 1 ^r a $xbarh a")
        .fft("O", λp: (p
            .record(g.fft("Oi"))
            .add_pt(0, 0.5, λ//-100)
            .mod_pt(2, -1, λ/-10)
            .mod_pt(2, -2, λ/30)
            .difference(DP(g.aperture.add(10, "mnx")))
            .pvl()
            .mod_pt(1, 0, λ/30)))
        .remove("Oi"))

@glyphfn(_O.w)
def _C(r, g):
    return (_CG(r, g)
        .remove("aperture", "beard")
        .fft("O", λp: (p
            .mod_pt(6, 0, λ/5)
            .mod_pt(7, 0, λ/-10)
            .mod_pt(5, 2, λ/5))))

@glyphfn(_C.w)
def _G(r, g):
    #return _CG(r, g)
    return (_CG(r, g)
        .append(DP("xbar", xbarr:=g.aperture * (g.bx.pc.x+10) // -50)
            .pvl()
            .mod_pt(1, 0, λ/-20))
        .fft("O", λp: (p
            .mod_pt(5, 0, λ/25)
            .mod_pt(5, 2, λ@xbarr.mxy)))
        .remove("beard", "aperture"))

@glyphfn(500)
def _S(r, g):
    return (g
        .set_width(g.c.stem*4.15)
        .register(
            hornl="-$stem -$earh+0",
            hornr="+$stem +$earh-10")
        .guide(
            bxx="i 0 $srfh",
            bxy="i $hdiag -$over",
            bxi=λg: DP(g.bxx).intersection(DP(g.bxy))
                .bounds().inset(-10).offset(10, 0))
        .record(DP("curve")
            .mt(g.hornr.ps)
            .bct(g.bxy.pn/-(stx:=30), "NE", start:=(0.65, 0.65))
            .bct(g.bxx.pnw, "NW", swing:=0.6)
            .bct(g.bxi.pse//(bigy:=55), ("SW", "NE"), big:=(0.65, 0.35))
            .bct(g.bxi.ps/(smallx:=15), "SE", small:=0.65)
            .bct(g.hornl.pne, g.bxi.psw, land:=0.65)
            .lt(g.hornl.pn)
            .bct(g.bxy.ps/stx, "SW", start)
            .bct(g.bxx.pse/10, "SE", swing)
            .bct(g.bxi.pnw//-bigy, ("NE", "SW"), big)
            .bct(g.bxi.pn/-smallx//5, "NW", small)
            .bct(g.hornr.psw, g.bxi.pne, land)
            .cp()))

@glyphfn()
def _U(r, g):
    c = 90
    return (g
        .add_stem()
        .register(
            caplƒ_ƒcapr="1 +$srfh ^c $srfw+20 $gap $srfw-60 a")
        .set_width(g.capr.mxx)
        .register(
            steml=f"-$stem 1 ^m =&capl.ps.x -$srfh+{c}",
            stemr=f"+$ldiag+10 1 ^m =&capr.ps.x -$srfh+{c}")
        .declare(sc:=g.steml.pse.i(g.stemr.psw) @ -g.c.over)
        .remove("stem")
        .record(DATPen("curve")
            .mt(g.steml.psw)
            .bct(sc, "SW", c:=0.75).bct(g.stemr.pse, "SE", c)
            .lt(g.stemr.psw)
            .bct(sc // g.c.srfh, "SE", c:=0.85).bct(g.steml.pse, "SW", c)
            .cp()))

@glyphfn(_U.w)
def _V(r, g):
    return (_U.func(r, g)
        .declare(
            hdl:=Line(g.capl.ps, y:=(g.bx.ps * g.capl.mxx)),
            ldl:=Line(g.capr.ps, y / (-g.c.hdiag * 0.16)))
        .ap(hdiag:=DP(hdl).ol(g.c.hdiag).ƒ(ldl, g.bx.ew))
        .ap(DP(ldl).ol(g.c.ldiag).ƒ(hdiag.sl(2), g.bx.ee))
        .remove("steml", "stemr", "curve"))

@glyphfn()
def _W(r, g):
    return (g
        .constants(srfw=g.c.srfw-50)
        .register(caplƒ_ƒcapmƒ_ƒcapr=
            "1 +$srfh ^c $srfw $gap $srfw-10 $gap $srfw-20 a")
        .declare(
            hdiag:=g.c.hdiag+-20,
            ldiag:=g.c.ldiag+15,
            hd1:=Line(g.capl.ps, p1:=g.capl.pse @ 0),
            hd2:=Line(p2:=g.capm.ps / 5, p3:=g.capm.pse @ 0),
            ld1:=Line(p1 / (nudge:=10), p2 / -25),
            ld2:=Line(p3 / (nudge), g.capr.ps))
        .ap(DP(hd1).ol(hdiag).ƒ(g.bx.ew, ~ld1))
        .ap(DP(hd2).ol(hdiag).ƒ(g.bx.ew, ~ld2))
        .ap(DP(ld1).ol(ldiag).ƒ(g.bx))
        .ap(DP(ld2).ol(ldiag).ƒ(g.bx)))

@glyphfn()
def _X(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{(f:=50)} $gap $srfw+{f} a",
            clƒ_ƒcr=f"1 +$srfh ^c $srfw+{f} $gap $srfw-{f} a")
        .set_width(g.br.mxx)
        .declare(
            hdl:=Line(g.cl.ps, g.br.pn))
        .ap(DP(hdl).ol(g.c.hdiag).ƒ(g.bx))
        .ap(DP(Line(g.bl.pn, hdl.t(0.5-(skew:=0.04))).extr(0.3))
            .ol(g.c.ldiag).ƒ(g.bx.ew, hdl))
        .ap(DP(Line(g.cr.ps, hdl.t(0.5+skew)).extr(0.3))
            .ol(g.c.ldiag).ƒ(g.bx.ee, hdl)))

@glyphfn()
def _Y(r, g):
    return (g
        .add_stem()
        .register(
            clƒ_ƒcr=f"1 +$srfh ^c $srfw+{(f:=50)} $gap $srfw-{f} a",
            base="1 -$srfh ^m -&cl.pc.x-10 ø ^m +&cr.pc.x+10 ø",
            stem=λg: g.stem % g.vs("=$hdiag -0.5 ^m =&base.pc.x ø"))
        .ap(DP("diagl", Line(g.cl.ps, g.base.pn // (yup:=120)))
            .ol(g.c.hdiag).ƒ(g.bx.ew, ~(fst:=g.stem.setmxy(g.bx.mxy)).ee))
        .ap(DP("diagr", Line(g.cr.ps, g.base.pn // (yup-30)))
            .ol(g.c.ldiag).ƒ(~g.bx.ee, fst.ew)))

@glyphfn()
def _Z(r, g:Glyph):
    diag = g.c.ldiag + 30
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            cap="1 +$srfh",
            base="1 -$srfh",
            eart="-$stem +$earh",
            earb="+$stem -$earh")
        .ap(DP(l:=Line(g.cap.pne // (d:=diag), g.base.psw // -d))
            .ol(diag).ƒ(g.bx))
        .ap(DP(g.cap).ƒ(g.bx.ew, g.bx.en, l))
        .ap(DP(g.base).ƒ(g.bx.ee, ~g.bx.es, ~l))
        .remove("cap", "base"))

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
            hdiag=f"$stem+{(n:=50)}",
            ldiag=f"$stem-{n}",
            srfw="$instem + $stem + $instem",
            nstem=f"$stem - {25}",
            ninstem=f"$instem - {20}",
            nbase="$ninstem*2 + $nstem",
            nshoulder=30,
            earh=λg: g.bx.divide(g.c.xbarh, "mdy")[0].h))

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
        DATPens([DP(g).translate(100, 100).f(None).s(hsl(random(), 1, a=0.25)).sw(5) for k,g in glyph.guides.items()]) if overlay else None,
        DATPen().rect(glyph.bounds()).f(None).s(hsl(0.7, a=0.3)).sw(5) if overlay else None,
        #DATPen().gridlines(r, 50, absolute=True) if overlay else None,
        (glyph.pen().skeleton(scale=4).f(None).s(hsl(0.57, 1, 0.47))) if overlay else None,
        glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.bounds().w+30, 0).f(0).s(None).color_phototype(r, blur=5),
        glyph.pen().removeOverlap().scale(0.5, center=Point([100, 100])).translate(glyph.bounds().w+30+glyph.bounds().w*0.75+30, 0).f(None).s(0).sw(3),
        lpts if overlay else None])
