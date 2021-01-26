from coldtype.test import *
from coldtype.grid import Grid

from fontTools.misc.bezierTools import splitLine

a = [(120, 230)]

class glyphfn():
    def __init__(self):
        self.w = 1000
        self.r = Rect(w, 750)

    def __call__(self, func):
        self.func = func
        self.name = func.__name__
        return self

def length(self):
    a2 = math.pow(self.start.x - self.end.x, 2)
    b2 = math.pow(self.start.y - self.end.y, 2)
    return math.sqrt(a2 + b2)

def tpx(self, tpx, limit=True):
    x = tpx * math.cos(self.angle())
    y = tpx * math.sin(self.angle())
    tp = self.start.offset(x, y)
    if not limit:
        return tp
    else:
        if Line(self.start, tp).length() > self.length():
            return self.end
        else:
            return tp

Line.length = length
Line.tpx = tpx


class Glyph(DATPens):
    def __init__(self):
        self.l = 20
        self.r = 20
        super().__init__()

    def addFrame(self, frame):
        super().addFrame(frame)
        setattr(self, "bx", frame)
        return self
    
    def set_width(self, width):
        self.addFrame(Rect(math.floor(width), self.bx.h))
        return self
    
    def spaced_frame(self):
        return self.bounds().expand(self.l+self.r, "mxx")
    
    setWidth = set_width
    
    def add_stem(self):
        return self.register(stem="-$stem 1 ^o $instem 0")
    
    @property
    def bxr(self):
        return DATPen().rect(self.bx)
    
    def brackets(self, bracks):
        self._brackets = bracks
        return self
    
    def realize(self):
        if hasattr(self, "_brackets"):
            for b in self._brackets:
                self.brack(*b)
        res = super().realize()
        return res.translate(self.l, 0).addFrame(self.spaced_frame())
    
    def all_guides(self):
        return DATPens([DP(x).translate(self.l, 0).f(None).s(hsl(random(), 1, a=0.25)).sw(10) for k,x in self.guides.items()])

    def brack(self, a, b, pt, y=None, c=None):
        x = self.c.brackw
        if not y:
            y = self.c.brackh
        if not c:
            c = self.c.brackc
        
        #print(a, b, pt, y, c)
        
        if isinstance(pt, str) and len(pt) == 2:
            apt = a.point(pt)
            
            if isinstance(b, Line):
                be = b
            else:
                be = b.ew if "W" in pt else b.ee
                if "N" in pt:
                    be = ~be
            
            opp = None
            if pt == "NE": opp = "SW"
            elif pt == "SW": opp = "NE"
            elif pt == "SE": opp = "NW"
            elif pt == "NW": opp = "SE"

            ctrl = a.edge(pt[0]) & be
            end = Line(ctrl, be.start).tpx(y)
            start = Line(ctrl, apt).tpx(x)
            
            r = Rect.FromPoints(ctrl, end, start)
            ri = r.expand(10, opp)
            #self.guide(apt)

            bracket = (DP("bracket", ri)
                .difference(DP()
                    .mt(start)
                    .bct(end, ctrl, c)
                    #.lt(Line(r.point(pt), ctrl).extr(.2).end)
                    .lt(ri.point(pt))
                    .cp()))
            return self.ap(bracket)

        else:
            if pt == "N":
                pt = ("NW", "NE")
            elif pt == "S":
                pt = ("SE", "SW")

            self.brack(a, b, pt[0], y, c)
            self.brack(a, b, pt[1], y, c)
            return self

@glyphfn()
def _A(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{(c:=20)} $gap $srfw+{c} a")
        .set_width(g.br.mxx)
        #.register(cap="-$srfw +$srfh")
        .declare(
            hd:=Line(g.br.pn, y:=g.bx.pn.setx(g.br.pnw.x) / 0),
            ld:=Line(g.bl.pn, y / (-g.c.hdiag*0.16)))
        .ap(dr:=DP("diagr", hd).ol(g.c.hdiag).ƒ(ld, ~g.bx.edge("mxx")))
        .ap(dl:=DP("diagl", ld).ol(g.c.ldiag).ƒ(g.bx))
        .ap(DP("xbar", Line(hd.t(t:=0.21), ld.t(t)))
            .ol(g.c.xbarh).ƒ(hd, ~ld))
        .guide(dl.sl(1))
        .brackets([
            (g.bl, dl.sl(1), "NW"),
            (g.br, ~dr.sl(4), "NE")]))

@glyphfn()
def _I(r, g):
    return (g
        .set_width(g.c.srfw+50)
        .register(
            base="1 -$srfh",
            cap="1 +$srfh",
            stem="=$stem 1")
        .brackets([
            (g.cap, g.stem, "S"),
            (g.base, g.stem, "N")
        ]))

@glyphfn()
def _J(r, g):
    return (g
        .setWidth(g.c.stem*4.25)
        .declare(c:=100)
        .register(
            stem=f"+$stem 1 ^o -$instem 0 ^s 0 -$srfh+{c}",
            ear=f"-$stem+20 -$earh+30 ^s 0 -$srfh+{c}",
            cap="+$srfw +$srfh ^e -30 0")
        .ap(DP()
            .mt(a:=g.stem.psw // 60)
            .bct(i:=a.i(0.5, g.ear.pne) @ g.c.srfh, "SE", c:=0.77)
            .bct(g.ear.pne, "SW", c+0.03)
            .lt(g.ear.pnw)
            .bct(i @ 0 / 0, "SW", c:=0.77)
            .bct(g.stem.pse, "SE", c-0.08)
            .cp()
            .pvl())
        .remove("ear")
        .brackets([(g.cap, g.stem, "S")]))

@glyphfn()
def _H(r, g, rn=0):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{rn} $gap $srfw+{rn} a",
            clƒ_ƒcr=f"1 +$srfh ^c $srfw-{rn} $gap $srfw+{rn} a",
            steml="-$stem 1 ^m =&bl.ps.x ø",
            stemr="-$stem 1 ^m =&br.ps.x ø",
            xbar="1 =$xbarh ^m -&steml.pc.x ø ^m +&stemr.pc.x ø")
        .brackets([
            (g.cl, g.steml, "S"),
            (g.cr, g.stemr, "S"),
            (g.bl, g.steml, "N"),
            (g.br, g.stemr, "N")]))

@glyphfn()
def _K(r, g):
    return (_H.func(r, g, rn=10)
        .ap(DP("udiag",
            udiag:=Line(g.steml.pc//-100, g.cr.ps).extr(0.1))
            .ol(g.c.ldiag+(cmp:=20)).ƒ(g.steml.ew, ~g.bx.ee))
        .append(DP("ldiag",
            Line(g.br.pn, g.cl.ps / 70).extr(0.12))
            .ol(g.c.hdiag-cmp).ƒ(udiag, [g.cr.pne, g.br.pse]))
        .remove("xbar", "stemr")
        #.guide(xx=g.fft("udiag").sl(3).reverse().tpx(150))
        .brackets([
            (g.cl, g.steml, "S"),
            (g.bl, g.steml, "N"),
            (g.cr, g.fft("udiag").sl(3), "SE"),
            (g.br, ~g.fft("ldiag").sl(2), "NE")
            ]))

@glyphfn()
def _E(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .register(
            baseƒ_ƒcap="r $srfh a $srfh",
            earbƒ_ƒeart="+$stem 1 ^r $earh a $earh",
            earb="&earb ^o 0 0",
            mid="1 =$xbarh ^m -&stem.pc.x ø ^m +&eart.psw.x-30 ø ^l +450 ø")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW"),
            (g.cap, g.eart, "SW"),
            (g.base, g.earb, "NW")]))

@glyphfn()
def _F(r, g):
    return (_E.func(r, g)
        .remove("earb")
        .register(base="-$srfw+10 -$srfh")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "N"),
            (g.cap, g.eart, "SW")
            ]))

@glyphfn()
def _L(r, g):
    return (g
        .set_width(g.c.stem*4.25)
        .add_stem()
        .register(
            base="1 -$srfh",
            cap="-$srfw +$srfh",
            earb="+$stem -$earh")
        .brackets([
            (g.cap, g.stem, "S"),
            (g.base, g.stem, "N")]))

@glyphfn()
def _T(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            base="=$srfw -$srfh",
            cap="1 +$srfh",
            earl="-$stem +$earh",
            earr="+$stem +$earh",
            stem="=$stem 1")
        .brackets([
            (g.cap, g.earl, "SE"),
            (g.cap, g.earr, "SW"),
            (g.base, g.stem, "N")])
        )

@glyphfn()
def _P(r, g, mod=None, tc=0.6, xc=0, ci=30, my=0):
    mh = g.c.xbarh + my
    if tc == 1:
        mh = g.c.srfh
    return (g
        .set_width(g.c.stem*4.5+xc)
        .add_stem()
        .guide(
            bxc=f"1 +{tc}",
            curve="&bxc ^m -&stem.mxx+50 ø",
            midƒknockƒcap=f"&bxc ^r {mh} a $srfh",
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
            .cp())
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "N")]))

@glyphfn()
def _B(r, g):
    return (_P.func(r, g, tc=0.56, my=-10, xc=0, ci=20, mod=λg: g
        .register(
            base=g.base.take(g.cap.w, "mnx")))
        .guide(
            bbxc=f"1 1 ^m -&curve.mnx +&knock.mny ^e +{(bnx:=30)} 0",
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
            .mod_pt(5, 0, (c:=20, 0))
            .mod_pt(6, 0, (c/2, 0)))
        .remove("base")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW")]))

@glyphfn()
def _D(r, g):
    # TODO mid inside mid-point is wrong b/c the knock is wrong
    return (_P.func(r, g, tc=1, xc=30, ci=50, mod=λg: g
        .register(mid="&mid ^m -0 ø"))
        .remove("base")
        .fft("curve", λc: c.pvl()
            .declare(q:=30)
            .mod_pt(8, 2, λ//q)
            .mod_pt(3, 2, λ//(q+10)))
        .guide(g.cap.es)
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW")
        ]))

@glyphfn()
def _R(r, g):
    return (_P.func(r, g, tc=0.55, xc=50, ci=50, my=0, mod=λg: g
        .register(
            base=g.base.subtract(20, "mxx"),
            #mid=g.mid.offset(0, 20).inset(10)
            )
        .guide(
            baser="+$srfw-70 -$srfh ^o 30 0")
        .ap(DP("leg")
            .mt(g.mid.pse/-20)
            .bct(g.baser.pnw, "NE", 0.65)
            .bct(g.baser.ps/20, "SW", 0.85)
            .lt(g.baser.pse)
            .lt(p:=g.baser.pne)
            .lt(p/-90)
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
            capr=g.capr.setlmnx((diag.sl(3) & g.capr.es).x + g.c.gap+5))
        .brackets([
            (g.capl, g.steml, "SW"),
            (g.capr, g.stemr, "S"),
            (g.base, g.steml, "N")]))

@glyphfn()
def _M(r, g):
    return (g
        .set_width(g.c.stem*6)
        .declare(
            spread:=-70,
            nosein:=50,
            wght:=g.c.hdiag-30)
        .register(
            _ƒstemlƒ_ƒstemr="c $ninstem $nstem a $nstem $ninstem",
            baselƒ_ƒbaser="1 -$srfh ^c $nbase a $nbase",
            caplƒ_ƒcapr=f"1 +$srfh ^c $nbase+{spread} a $nbase+{spread}")
        .ap(diagl:=DP("dgl",
            ddl:=Line(g.capl.pne, g.bx.ps / nosein))
            .ol(wght).ƒ(g.bx))
        .ap(diagr:=DP("dgr",
            Line(g.capr.pnw, g.bx.ps / -nosein))
            .ol(wght).ƒ(g.bx))
        .guide(diagl.sl(2))
        .fft("dgl", λ.ƒ(diagr.sl(0), ~g.bx.edge("mnx")))
        .fft("dgr", λ.ƒ(diagl.sl(0), ~g.bx.edge("mxx")))
        .brackets([
            (g.capl, g.steml, "SW"),
            (g.basel, g.steml, "N"),
            (g.capr, g.stemr, "SE"),
            (g.baser, g.stemr, "N")
        ]))

@glyphfn()
def _O(r, g, clx=0):
    (g.set_width(g.c.stem*4.25)
        .constants(
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

@glyphfn()
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
            #.add_pt(0, 0.5, λ//-100)
            #.mod_pt(2, -1, λ/-10)
            #.mod_pt(2, -2, λ/30)
            .difference(DP(g.aperture.add(10, "mnx")))
            .mod_pt(11, 0, (n:=-50, 0))
            .mod_pt(12, 0, (n, -70))
            .pvl()
            .mod_pt(1, 0, λ/30)))
        .remove("Oi"))

@glyphfn()
def _C(r, g):
    return (_CG(r, g)
        .remove("aperture", "beard")
        .fft("O", λp: (p
            .mod_pt(6, 0, λ/5)
            .mod_pt(7, 0, λ/-10)
            .mod_pt(5, 2, λ/5))))

@glyphfn()
def _G(r, g):
    #return _CG(r, g)
    return (_CG(r, g)
        .append(DP("xbar", xbarr:=g.aperture * (g.bx.pc.x+10) // -50)
            .pvl()
            .mod_pt(1, 0, λ/-20))
        .fft("O", λp: (p
            .mod_pt(4, 0, λ/25)
            .mod_pt(4, 2, λ@xbarr.mxy)))
        .remove("beard", "aperture"))

@glyphfn()
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
            .bct(g.bxi.pn/-smallx//(adj:=5), "NW", small)
            .bct(g.hornr.psw, g.bxi.pne//adj, land)
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
        .declare(sc:=g.steml.pse.i(0.47, g.stemr.psw) @ -g.c.over)
        .remove("stem")
        .record(DATPen("curve")
            .mt(g.steml.psw)
            .bct(sc, "SW", c:=0.75)
            .bct(g.stemr.pse, "SE", c)
            .lt(g.stemr.psw)
            .bct(sc // g.c.srfh, "SE", c:=0.90)
            .bct(g.steml.pse, "SW", c)
            .cp())
        .brackets([
            (g.capl, g.steml, "S"),
            (g.capr, g.stemr, "S")]))

@glyphfn()
def _V(r, g):
    return (_U.func(r, g)
        .declare(
            hdl:=Line(g.capl.ps, y:=(g.bx.ps * g.capl.mxx)),
            ldl:=Line(g.capr.ps, y / 0))
        .ap(hdiag:=DP(hdl).ol(g.c.hdiag).ƒ(ldl, g.bx.ew))
        .ap(ldiag:=DP(ldl).ol(g.c.ldiag).ƒ(hdiag.sl(2), g.bx.ee))
        .remove("steml", "stemr", "curve")
        .guide(hdiag.sl(2), ldiag.sl(0))
        .brackets([
            (g.capl, ~hdiag.sl(2), "SW"),
            (g.capl, hdiag.sl(0), "SE"),
            (g.capr, ~ldiag.sl(2), "SW"),
            (g.capr, ldiag.sl(0), "SE")]))

@glyphfn()
def _W(r, g):
    return (g
        .constants(srfw=g.c.srfw-50)
        .register(caplƒ_ƒcapmƒ_ƒcapr=
            "1 +$srfh ^c $srfw $gap $srfw-10 $gap $srfw-20 a")
        .set_width(g.capr.mxx)
        .declare(
            hdiag:=g.c.hdiag+-20,
            ldiag:=g.c.ldiag+15,
            hd1:=Line(g.capl.ps, p1:=g.capl.pse @ 0),
            hd2:=Line(p2:=g.capm.ps / 5, p3:=g.capm.pse @ 0),
            ld1:=Line(p1 / (nudge:=10), p2 / -25),
            ld2:=Line(p3 / (nudge), g.capr.ps))
        .ap(hd1:=DP(hd1).ol(hdiag).ƒ(g.bx.ew, ~ld1))
        .ap(hd2:=DP(hd2).ol(hdiag).ƒ(g.bx.ew, ~ld2))
        .ap(ld1:=DP(ld1).ol(ldiag).ƒ(g.bx))
        .ap(ld2:=DP(ld2).ol(ldiag).ƒ(g.bx))
        #.guide(ld1.sl(0))
        .brackets([
            (g.capl, ~hd1.sl(2), "SW"),
            (g.capl, hd1.sl(0), "SE"),
            (g.capm, ~ld1.sl(0), "SW"),
            (g.capm, hd2.sl(0), "SE"),
            (g.capr, ~ld2.sl(0), "SW"),
            (g.capr, ld2.sl(2), "SE")
        ]))

@glyphfn()
def _X(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$srfh ^c $srfw-{(f:=50)} $gap $srfw+{f} a",
            clƒ_ƒcr=f"1 +$srfh ^c $srfw+{f} $gap $srfw-{f} a")
        .set_width(g.br.mxx)
        .declare(
            hdl:=Line(g.cl.ps, g.br.pn))
        .ap(hdlp:=DP(hdl).ol(g.c.hdiag).ƒ(g.bx))
        .ap(ldlp1:=DP(Line(g.bl.pn, hdl.t(0.5-(skew:=0.04))).extr(0.3))
            .ol(g.c.ldiag).ƒ(g.bx.ew, hdl))
        .ap(ldlp2:=DP(Line(g.cr.ps, hdl.t(0.5+skew)).extr(0.3))
            .ol(g.c.ldiag).ƒ(g.bx.ee, hdl))
        .guide(ldlp1.sl(1))
        .brackets([
            (g.cl, ~hdlp.sl(2), "SW"),
            #(g.cl, hdlp.sl(0), "SE"),
            (g.bl, ldlp1.sl(1), "NW"),
            #(g.bl, ~ldlp1.sl(3), "NE"),
            #(g.cr, ~ldlp2.sl(3), "SW"),
            (g.cr, ldlp2.sl(1), "SE"),
            #(g.br, hdlp.sl(2), "NW"),
            (g.br, ~hdlp.sl(0), "NE")
        ]))

@glyphfn()
def _Y(r, g):
    return (g
        .add_stem()
        .register(
            clƒ_ƒcr=f"1 +$srfh ^c $srfw+{(f:=50)} $gap $srfw-{f} a",
            base="1 -$srfh ^m -&cl.pc.x-10 ø ^m +&cr.pc.x+10 ø",
            stem=λg: g.stem % g.vs("=$hdiag -0.5 ^m =&base.pc.x ø"))
        .ap(diagl:=DP("diagl",
            Line(g.cl.ps, g.base.pn // (yup:=120)))
            .ol(g.c.hdiag).ƒ(g.bx.ew, ~(fst:=g.stem.setmxy(g.bx.mxy)).ee))
        .ap(diagr:=DP("diagr",
            Line(g.cr.ps, g.base.pn // (yup-30)))
            .ol(g.c.ldiag).ƒ(~g.bx.ee, fst.ew))
        .guide(diagl.sl(3))
        .brackets([
            (g.base, g.stem, "N"),
            (g.cl, ~diagl.sl(3), "SW"),
            (g.cr, diagr.sl(0), "SE")]))

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
        .remove("cap", "base")
        .brackets([
            (g.cap, g.eart, "SE"),
            (g.base, g.earb, "NW")
        ]))

class font(animation):
    def __init__(self, rect=(2000, 1000)):
        self.glyphs = []
        for k, v in globals().items():
            if isinstance(v, glyphfn):
                self.glyphs.append(v)
        self.glyphs.sort(key=lambda a: a.name)
        super().__init__(rect, timeline=Timeline(len(self.glyphs)), rstate=1)
    
    def fn_to_frame(self, fn_name):
        for idx, g in enumerate(self.glyphs):
            if g.name == fn_name:
                return idx

def build_glyph(cap):
    g = (Glyph()
        .addFrame(cap.r)
        .constants(
            srfh=190,
            stem=115,
            instem=105,
            xbarh=100,
            over=10,
            gap=20,
            hdiag=f"$stem+{(n:=30)}",
            ldiag=f"$stem-{n}",
            srfw="$instem + $stem + $instem",
            nstem=f"$stem - {15}",
            ninstem=f"$instem - {30}",
            nbase="$ninstem*2 + $nstem",
            nshoulder=15,
            earh=λg: g.bx.divide(g.c.xbarh, "mdy")[0].h,
            brackw=30,
            brackh=60,
            brackc=0.75))

    glyph = (cap.func(Rect(1080, 1080), g)
        .realize()
        .f(None)
        .s(0)
        .sw(2))
    
    return glyph

@font()
def single_char(f, rs):
    r = f.a.r
    
    glyph = build_glyph(single_char.glyphs[f.i])
    g = glyph
    
    if False:
        #print(glyph.pen().removeOverlap().round(0).printvl())
        ufo = raw_ufo(__sibling__("_test_fluent_drawing.ufo"))
        glyph_name = cap.func.__name__.strip("_")
        gp = glyph.pen()-.removeOverlap().round(0)
        ufo_glyph = gp.to_glyph(name=glyph_name, width=gp.bounds().w+glyph.r)
        ufo.insertGlyph(ufo_glyph)
        ufo.save()

    glyph.translate(100, 100) # for display
    overlay = Overlay.Info in rs.overlays

    lpts = DATPens()
    txtstyle = Style("Times", 18, load_font=0, fill=hsl(0.5, 0.5))

    for p in glyph:
        if "bracket" not in p.getTag():
            for idx, (mv, pts) in enumerate(p.value):
                if len(pts) > 0:
                    for jdx, pt in enumerate(pts):
                        lpts += DATText(f"{idx},{jdx}", txtstyle, Rect.FromCenter(pt, 20).offset(20, 20))

    return DATPenSet([
        glyph.copy().f(None).s(0, 0.5).sw(5) if overlay else None,
        glyph.pen().removeOverlap().f(None).s(0, 1).sw(5) if not overlay else None,
        DATPen().rect(glyph.bounds()).f(None).s(hsl(0.9, a=0.3)).sw(5) if overlay else None,
        glyph.all_guides().translate(100, 100) if overlay else None,
        DATPen(glyph.spaced_frame()).translate(-g.l, 0).f(None).s(hsl(0.7, a=0.3)).sw(5) if overlay else None,
        #DATPen().gridlines(r, 50, absolute=True) if overlay else None,
        #(glyph.pen().skeleton(scale=4).f(None).s(hsl(0.57, 1, 0.47))) if overlay else None,
        #(glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.getFrame().w+30, 0).f(0).s(None).color_phototype(r, blur=5)),
        ßshow(glyph.pen().removeOverlap()
            .scale(0.75, center=Point([100, 100]))
            .translate(
                glyph.getFrame().w+30
                #+ glyph.bounds().w*0.75+30
                , 0
                )
            .f(hsl(0.65, s=1, l=0.8, a=0.25)).s(0).sw(3)),
        lpts if overlay else None
        ])

@renderable(rect=(2000, 400), rstate=1)
def test_string(r, rs):
    xa = 0
    out = DPS()
    for i in [7, 9]:
        glyph = build_glyph(single_char.glyphs[i])
        out += (glyph
            .pen()
            .removeOverlap()
            .s(None)
            .f(0)
            .scale(0.25, center=r.inset(100).psw)
            .translate(xa, 0))
        xa += glyph.getFrame().w * 0.25
    return out