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
        self.l = 10
        self.r = 10
        self.name = None
        super().__init__()
    
    def glyph_name(self, name):
        self.name = name
        return self
    
    def space(self, l, r):
        self.l = l
        self.r = r
        return self

    def addFrame(self, frame):
        super().addFrame(frame)
        setattr(self, "bx", frame)
        return self
    
    def set_width(self, width):
        self.addFrame(Rect(math.floor(width), self.bx.h))
        return self
    
    def spaced_frame(self):
        if "empty" in self.guides:
            return self.getFrame().expand(self.l+self.r, "mxx")
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
        dps = DATPens()
        for idx, (k, x) in enumerate(self.guides.items()):
            dps += (DP(x)
                .translate(self.l, 0)
                .f(None)
                .s(hsl(idx/2.3, 1, a=0.25)).sw(10))
        return dps

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
def A(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$sfhb ^c $sfw-{(c:=20)} $gap $sfw+{c} a")
        .set_width(g.br.mxx)
        .register(cap="1 +$sfht ^i $instem 0")
        .declare(
            hd:=Line(g.br.pn, y:=g.bx.pn.setx(g.br.pnw.x) / 0),
            ld:=Line(g.bl.pn, y / (-g.c.hdiag*0.16)))
        .ap(dr:=DP("diagr", hd).ol(g.c.hdiag).ƒ(ld, ~g.bx.edge("mxx")))
        .ap(dl:=DP("diagl", ld).ol(g.c.ldiag).ƒ(g.bx))
        .ap(DP("xbar", Line(hd.t(t:=0.21), ld.t(t)))
            .ol(g.c.xbarh-10).ƒ(hd, ~ld))
        #.guide(dl.sl(1))
        .brackets([
            (g.bl, dl.sl(1), "NW"),
            (g.br, ~dr.sl(4), "NE")]))

@glyphfn()
def I(r, g):
    return (g
        .set_width(g.c.stem*3)
        .register(
            base="1 -$sfhb",
            cap="1 +$sfht",
            stem="=$stem 1")
        .brackets([
            (g.cap, g.stem, "S"),
            (g.base, g.stem, "N")
        ]))

@glyphfn()
def J(r, g):
    return (g
        .setWidth(g.c.stem*4.25)
        .declare(c:=100)
        .register(
            stem=f"+$stem 1 ^o -$instem 0 ^s 0 -$sfhb+{c}",
            ear=f"-$stem+20 -$earhb+30 ^s 0 -$sfhb+{c}",
            cap="+$sfw +$sfht ^e -30 0")
        .ap(DP()
            .mt(a:=g.stem.psw // 60)
            .bct(i:=a.i(0.5, g.ear.pne) @ g.c.sfhb, "SE", c:=0.77)
            .bct(g.ear.pne, "SW", c+0.03)
            .lt(g.ear.pnw)
            .bct(i @ 0 / 0, "SW", c:=0.77)
            .bct(g.stem.pse, "SE", c-0.08)
            .cp()
            .pvl())
        .remove("ear")
        .brackets([(g.cap, g.stem, "S")]))

@glyphfn()
def H(r, g, rn=0):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$sfhb ^c $sfw-{rn} $gap $sfw+{rn} a",
            clƒ_ƒcr=f"1 +$sfht ^c $sfw-{rn} $gap $sfw+{rn} a",
            steml="-$stem 1 ^m =&bl.ps.x ø",
            stemr="-$stem 1 ^m =&br.ps.x ø",
            xbar="s 0 -$earhb ^s 0 +$earht ^t 1 =$xbarh ^m -&steml.pc.x ø ^m +&stemr.pc.x ø")
        .brackets([
            (g.cl, g.steml, "S"),
            (g.cr, g.stemr, "S"),
            (g.bl, g.steml, "N"),
            (g.br, g.stemr, "N")]))

@glyphfn()
def K(r, g):
    return (H.func(r, g, rn=10)
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
            (g.br, ~g.fft("ldiag").sl(3), "NE")
            ]))

@glyphfn()
def E(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .register(
            baseƒ_ƒcap="r $sfhb a $sfht",
            earbƒcenterƒeart="+$stem 1 ^r $earhb-20 a $earht-20",
            earb="&earb ^o 0 0",
            center="&center ^m -&stem.pc.x ø ^m +&eart.psw.x-40 ø ^t 1 =$xbarh")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW"),
            (g.cap, g.eart, "SW"),
            (g.base, g.earb, "NW")]))

@glyphfn()
def F(r, g):
    return (E.func(r, g)
        .remove("earb")
        .register(
            center="&center ^o 0 -20",
            base="&base ^m +&center.mxx+10 ø")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "N"),
            (g.cap, g.eart, "SW")]))

@glyphfn()
def L(r, g):
    return (g
        .set_width(g.c.stem*4.25)
        .add_stem()
        .register(
            base="1 -$sfhb",
            cap="-$sfw +$sfht",
            earb="+$stem -$earhb*1.1")
        .brackets([
            (g.cap, g.stem, "S"),
            (g.base, g.stem, "N")]))

@glyphfn()
def T(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            base="=$sfw -$sfhb",
            cap="1 +$sfht",
            earl="-$stem +$earhb",
            earr="+$stem +$earhb",
            stem="=$stem 1")
        .brackets([
            (g.cap, g.earl, "SE"),
            (g.cap, g.earr, "SW"),
            (g.base, g.stem, "N")])
        )

@glyphfn()
def P(r, g, mod=None, xc=0, ci=30, my=0, mn=0):
    mh = g.c.xbarh + my
    return (g
        .set_width(g.c.stem*4.5+xc)
        .add_stem()
        .guide(
            center="s 0 -$sfhb ^s 0 +$sfhb ^t 1 =$xbarh",
            bxc=f"s 0 -&center.mny+{mn}",
            _curve="&bxc ^m -&stem.mxx+50 ø",
            _midƒ_knockƒ_cap=f"&bxc ^r {mh} a $sfht",
            _knock=f"&knock ^s +$stem+{ci} 0",
            _mid="&mid ^m -&stem.pc.x ø ^m +&curve.mnx ø",
            _cap="&cap ^m +&curve.mnx ø")
        .register(
            base="-$sfw+10 -$sfhb")
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
def B(r, g):
    return (P.func(r, g, my=0, mn=30, xc=0, mod=λg: (g
        .register(
            base=g.base.take(g.cap.w, "mnx")))
        .guide(
            _bbxc=f"1 1 ^m -&curve.mnx +&knock.mny ^e +{(bnx:=30)} 0",
            _bknock=f"&bbxc ^m +&knock.mxx+{bnx*1} -&base.mxy ^m ø +&mid.mny"))
        .ap(DP("belly")
            .declare(
                n:=18,
                cif:=g.c.cicf-0.02,
                cof:=g.c.cocf+0.02)
            .mt(lp:=g.mid.pse)
            .bct(g.bknock.pe, "NE", cif)
            .bct(g.bknock.psw, "SE", cif)
            .lt(g.base.pnw, g.base.psw, g.base.pse)
            .bct(g.bbxc.pe/30, "SE", cof)
            .bct(g.mid.pne, "NE", cof)
            .cp()
            .mod_pt(5, 0, (c:=20, 0))
            .mod_pt(6, 0, (c/2, 0)))
        .fft("curve", λp: (p
            .declare(n:=30) # TODO good example of a "re-tune curve" function
            .mod_pt(8, 2, (0, n/3))
            .mod_pt(8, 1, (0, n))
            .mod_pt(8, 0, (-n, 0))))
        .remove("base")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW")]))

@glyphfn()
def D(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .guide(
            baseƒgapƒcap="r $sfhb a $sfht",
            stemr="+$stem+30 1",
            knck="&gap ^m -&stem.mxx+20 ø ^m +&stemr.mnx ø")
        .ap(DP("curve")
            .mt(g.cap.psw)
            .lt(g.knck.pnw)
            .bct(g.knck.pe, "NE", (ic:=0.75))
            .bct(g.knck.psw, "SE", ic)
            .lt(g.base.pnw, g.base.psw, g.stem.pse)
            .bct(g.stemr.pe, "SE", (oc:=0.7))
            .bct(g.stem.pne, "NE", oc)
            .lt(g.cap.pnw)
            .cp()))

@glyphfn()
def R(r, g):
    return (P.func(r, g, xc=0, my=10, mn=40, mod=λg: g
        .register(
            base=g.base.subtract(20, "mxx"),
            #mid=g.mid.offset(0, 20).inset(10)
            )
        .guide(
            baser="+$sfw -$sfhb ^o 60 0")
        .ap(DP("leg")
            .mt(g.mid.pse/-30)
            .bct(brs:=g.base.pne/(g.c.gap+10), "NE", 0.65)
            .bct(brs/(g.c.stem+10)@0, "SW", 0.85)
            .lt(g.baser.pse)
            .lt(p:=g.baser.pne)
            .lt(brs/(g.c.stem+25))
            .bct(g.mid.pse.o(50, 20), "NE", 0.65)
            .cp()
            .translate(0, 0))))

@glyphfn()
def N(r, g):
    return (g
        .set_width(int(g.c.stem*5.25))
        .guide(caplƒ_ƒcapr="1 +$sfht ^c $nsfw a $nsfw")
        .register(
            _ƒstemlƒ_ƒstemr="c $ninstem $nstem a $nstem $ninstem",
            base="-$nsfw -$sfhb",
            capr="&capr",
            capl="&capl ^m +&steml.mxx ø")
        .guide(
            l1=Line((g.steml.ee & g.capl.es)//-20, g.base.pne/30),
            l2=λg: g.l1.offset(min(g.c.hdiag+40, g.capr.psw.x-g.l1[0].x-g.c.gap), 0))
        .ap(DP("diag2")
            .mt(g.l1 & g.steml.ee, g.l1 & g.bx.es, g.stemr.ps)
            .lt(g.l2 & g.stemr.ecx, g.l2 & g.bx.en, g.capl.pn).cp())
        .brackets([
            (g.capl, g.steml, "SW"),
            (g.capr, g.stemr, "S"),
            (g.base, g.steml, "N")]))

@glyphfn()
def M(r, g):
    return (g
        .set_width(g.c.stem*6.10)
        .declare(wght:=g.c.hdiag-15)
        .guide(
            gcaplƒ_ƒgcapr=f"1 +$sfht ^c $nsfw a $nsfw",
            base="1 -$sfhb")
        .register(
            _ƒstemlƒ_ƒstemr="c $ninstem $nstem a $nstem $ninstem",
            baselƒ_ƒbaser="1 -$sfhb ^c $nsfw a $nsfw",
            capl="&gcapl ^m +&steml.mxx ø",
            capr="&gcapr ^m -&stemr.mnx ø")
        .guide(
            l1=Line((g.capl.es & g.steml.ee)//(n:=-60), g.basel.pne/g.c.gap),
            l1o=λ.l1.offset(wght, 0),
            l2=Line((g.capr.es & g.stemr.ew)//n, g.baser.pnw/-g.c.gap),
            l2o=λ.l2.offset(-wght, 0))
        .ap(DP("dl")
            .mt(g.l1 & g.bx.en, g.l1 & g.bx.es)
            .lt(g.l2 & g.bx.es, g.l2 & g.bx.en)
            .lt(g.l2o & g.bx.en, g.l2o & g.base.en)
            .lt(g.l1o & g.base.en)
            .lt(g.l1o & g.bx.en))
        .brackets([
            (g.capl, g.steml, "SW"),
            (g.basel, g.steml, "N"),
            (g.capr, g.stemr, "SE"),
            (g.baser, g.stemr, "N")]))

@glyphfn()
def O(r, g, clx=0):
    (g.set_width(g.c.stem*4.15)
        .space(n:=g.l+5, n)
        .constants(
            hw=g.c.stem+35)
        .guide(
            #o=g.bx.inset(0, -g.c.over*1.2),
            o="i 0 -$over",
            i="i $hw 0 ^s 0 +$sfht ^s 0 -$sfhb"))

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
        .ap(o(g.o, 40, 0.65).tag("O"))
        .ap(~o(g.i, 16, 0.85).tag("Oi")))

@glyphfn()
def Q(r, g):
    return (O.func(r, g)
        .guide(quill="=$stem -$sfhb ^o 0 -$sfhb*0.5 ^m =&i.mxx ø")
        .ap(DP(g.quill).rotate(23)))

def _CG(r, g):
    return (g
        .set_width(g.c.stem*4)
        .guide(
            _stemlƒ_cntryƒ_stemr="i 0 -$over ^c $stem+30 a $stem-10",
            knckbƒ_ixbarƒknckt="&cntry ^s 0 -$sfhb ^s 0 +$sfht ^r a $xbarh a",
            _oxbar="&ixbar ^m -0 ø ^m +&stemr.mxx ø")
        .register(
            eart="&stemr ^m ø -&ixbar.mxy")
        .ap(DP("curve")
            .mt(g.oxbar.pne/(-g.stemr.w/2))
            .bct(g.cntry.pn/-20, "NE", (oc:=0.71))
            .bct(g.oxbar.pnw//-(n:=30), "NW", oc)
            .lt(g.oxbar.psw//n)
            .bct(g.cntry.ps/-10, "SW", oc)
            .bct(g.oxbar.pse, "SE", oc)
            .lt(g.ixbar.pse)
            .bct(g.knckb.ps/-5, g.knckb.pse/-10, (ic:=0.85)-0.01)
            .bct(g.ixbar.psw//(n*0.5), "SW", ic)
            .lt(g.ixbar.pnw//(-n*0.5))
            .bct(g.knckt.pn, "NW", ic)
            .bct(g.ixbar.pne, "NE", ic)
            .cp()))

@glyphfn()
def C(r, g):
    return (_CG(r, g))

@glyphfn()
def G(r, g):
    return (_CG(r, g)
        .guide(xbar="&ixbar ^o 0 -$gap*2 ^m -&knckb.pc.x-20 ø ^m +&stemr.mxx ø")
        .guide(south=Rect.FromCenter(g.cntry.ps, 50))
        .ap(DP(g.xbar).mod_pt(1, 0, λp: p * g.stemr.pc.x))
        .fft("curve", λp: (p
            .mod_pt(5, 2, λp: p @ g.xbar.mxy)
            .mod_pt(5, 1, (0, -10)))))

@glyphfn()
def S(r, g):
    return (g
        .set_width(g.c.stem*4.15)
        .register(
            earb="-$stem -$earhb+0",
            eart="+$stem +$earht")
        .guide(
            tbx=f"1 +&eart.h ^o 0 -$sfht/5",
            bbx=f"1 -&earb.h ^o 0 $sfhb/5",
            _bxy="i $hdiag -$over",
            _bxi="i $hdiag $over*0.75 ^s 0 -$sfhb ^s 0 +$sfht ^o 15 0 ^i 10 -30")
        .record(DP("curve")
            .mt(g.eart.ps)
            .bct(g.bxy.pn/-(stx:=30), "NE", start:=(0.59, 0.65))
            .bct(g.tbx.pw, "NW", swing:=0.6)
            .bct(g.bxi.pse//(bigy:=55), ("SW", "NE"), big:=(0.62, 0.37))
            .bct(g.bxi.ps/(smallx:=25), "SE", small:=0.57)
            .bct(g.earb.pne, g.bxi.psw, land:=0.65)
            .lt(g.earb.pn)
            .bct(g.bxy.ps/stx, "SW", start)
            .bct(g.bbx.pe/20, "SE", swing)
            .bct(g.bxi.pnw//-bigy, ("NE", "SW"), big)
            .bct(g.bxi.pn/-smallx//(adj:=5), "NW", small)
            .bct(g.eart.psw, g.bxi.pne//adj, land)
            .cp()))

@glyphfn()
def U(r, g):
    c = 90
    return (g
        .add_stem()
        .register(
            caplƒ_ƒcapr="1 +$sfht ^c $sfw+20 $gap $sfw-60 a")
        .set_width(g.capr.mxx)
        .register(
            steml=f"-$stem 1 ^m =&capl.ps.x -$sfhb+{c}",
            stemr=f"+$ldiag+10 1 ^m =&capr.ps.x -$sfhb+{c}")
        .guide(
            center="m -&steml.mxx --$over ^m +&stemr.mnx ø",
            knock="&center ^m ø -$sfhb")
        #.declare(sc:=g.steml.pse.i(0.47, g.stemr.psw) @ -g.c.over)
        .remove("stem")
        .record(DATPen("curve")
            .mt(g.steml.psw)
            .bct(g.center.ps, "SW", c:=0.75)
            .bct(g.stemr.pse, "SE", c)
            .lt(g.stemr.psw)
            .bct(g.knock.ps, "SE", c:=0.90)
            .bct(g.steml.pse, "SW", c)
            .cp())
        .brackets([
            (g.capl, g.steml, "S"),
            (g.capr, g.stemr, "S")]))

@glyphfn()
def V(r, g):
    return (U.func(r, g)
        .guide(center="&center ^m ø -0")
        .declare(
            hdl:=Line(g.capl.ps, y:=(g.center.ps)),
            ldl:=Line(g.capr.ps, y / 0))
        .ap(hdiag:=DP(hdl).ol(g.c.hdiag).ƒ(ldl, g.bx.ew))
        .ap(ldiag:=DP(ldl).ol(g.c.ldiag).ƒ(hdiag.sl(3), g.bx.ee))
        .remove("steml", "stemr", "curve")
        .guide(hdiag.sl(2), ldiag.sl(0))
        .brackets([])
        .brackets([
            (g.capl, ~hdiag.sl(3), "SW"),
            (g.capl, hdiag.sl(0), "SE"),
            (g.capr, ~ldiag.sl(2), "SW"),
            (g.capr, ldiag.sl(0), "SE")
            ]))

@glyphfn()
def W(r, g):
    return (g
        .constants(sfw=g.c.sfw-50)
        .register(caplƒ_ƒcapmƒ_ƒcapr=
            "1 +$sfht ^c $sfw $gap $sfw-10 $gap $sfw-20 a")
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
def X(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"1 -$sfhb ^c $sfw-{(f:=20)} $gap $sfw+{f} a",
            clƒ_ƒcr=f"1 +$sfht ^c $sfw+{f} $gap $sfw-{f} a")
        .set_width(g.br.mxx)
        .declare(
            hdl:=Line(g.cl.ps, g.br.pn))
        .ap(hdlp:=DP(hdl).ol(g.c.hdiag).ƒ(g.bx))
        .ap(ldlp1:=DP(Line(g.bl.pn, hdl.t(0.5-(skew:=0.06))).extr(0.3))
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
def Y(r, g):
    return (g
        .add_stem()
        .register(
            clƒ_ƒcr=f"1 +$sfht ^c $sfw+{(f:=50)} $gap $sfw-{f} a",
            base="1 -$sfhb ^m -&cl.pc.x-10 ø ^m +&cr.pc.x+10 ø",
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
def Z(r, g:Glyph):
    diag = g.c.ldiag + 30
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            cap=f"1 +$sfht ^s -{(xti:=30)} 0",
            base="1 -$sfhb",
            eart=f"-$stem +$earht ^o {xti} 0",
            earb="+$stem -$earhb")
        .ap(DP(l:=Line(g.cap.pne // (d:=diag), g.base.psw // -d))
            .ol(diag).ƒ(g.bx))
        .ap(DP(g.cap).ƒ(g.bx.ew, g.bx.en, l))
        .ap(DP(g.base).ƒ(g.bx.ee, ~g.bx.es, ~l))
        .remove("cap", "base")
        .brackets([
            (g.cap, g.eart, "SE"),
            (g.base, g.earb, "NW")]))

@glyphfn()
def space(r, g):
    return (g
        .set_width(g.c.stem*2)
        .space(0, 0)
        .guide(empty=g.bx))

class font(animation):
    def __init__(self, rect=(2000, 1200)):
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
    
    def char_to_frame(self, c):
        return self.fn_to_frame(uni_to_glyph(ord(c)))
    
    def glyph_view(self, r, glyph, compare, overlay=False):
        lpts = DATPens()
        txtstyle = Style("Times", 18, load_font=0, fill=hsl(0.5, 0.5))

        for p in glyph:
            if "bracket" not in p.getTag():
                for idx, (mv, pts) in enumerate(p.value):
                    if len(pts) > 0:
                        for jdx, pt in enumerate(pts):
                            lpts += DATText(f"{idx},{jdx}", txtstyle, Rect.FromCenter(pt, 20).offset(20, 20))

        return DATPens([
            glyph.copy().f(None).s(0, 0.5).sw(5) if overlay else None,
            glyph.pen().removeOverlap().f(None).s(0, 1).sw(5) if not overlay else None,
            DATPen().rect(glyph.bounds()).f(None).s(hsl(0.9, a=0.3)).sw(5) if overlay else None,
            glyph.all_guides() if overlay else None,
            DATPen(glyph.spaced_frame()).translate(-glyph.l, 0).f(None).s(hsl(0.7, a=0.3)).sw(5) if overlay else None,
            DPS([
                DP(r.es).s(0).sw(1),
                DP(r.take(750, "mny").en).s(0).sw(1),
            ]) if overlay else None,
            #DATPen().gridlines(r, 50, absolute=True) if overlay else None,
            (glyph.pen().skeleton(scale=4).f(None).s(hsl(0.57, 1, 0.47))) if overlay else None,
            #(glyph.pen().removeOverlap().scale(0.75, center=Point([100, 100])).translate(glyph.getFrame().w+30, 0).f(0).s(None).color_phototype(r, blur=5)),
            ßshow(glyph.pen().removeOverlap()
                .scale(0.75, center=Point([0, 0]))
                .translate(
                    glyph.getFrame().w+30
                    #+ glyph.bounds().w*0.75+30
                    , 0
                    )
                .f(hsl(0.65, s=1, l=0.8, a=0.75))
                .s(0).sw(3)
                .s(None)
                ),
            lpts if overlay else None,
            (build_glyph(
                single_char.glyphs[single_char.char_to_frame(compare)])
                .scale(0.75, center=Point([0, 0]))
                .translate(glyph.spaced_frame().w+30, 0)
                .pen()
                .removeOverlap()
                .f(hsl(0.9, a=0.25))
                .s(None)) if compare else None
            ])
    
    def test_string(self, scale, txt):
        out = DPS()
        if txt:
            cidxs = [single_char.fn_to_frame(uni_to_glyph(ord(c))) for c in txt.upper()]

            xa = 0
            for i in cidxs:
                if i is None:
                    continue
                glyph = build_glyph(single_char.glyphs[i])
                out += (glyph
                    .pen()
                    .removeOverlap()
                    .s(0).sw(2)
                    .f(hsl(0.9, a=0.1))
                    .scale(scale, center=Point([0, 0]))
                    .translate(xa, 0))
                xa += glyph.getFrame().w * scale
        return out

def build_glyph(cap):
    g = (Glyph()
        .addFrame(cap.r)
        .space(n:=10, n)
        .glyph_name(cap.func.__name__)
        .constants(
            _sfh=170,
            sfhb=λ.c._sfh+40,
            sfht=λ.c._sfh-40,
            earhb="$sfhb*1.75",
            earht="$sfht*2.25",
            stem=115,
            instem=λ.c.stem - 10,
            xbarh=100,
            over=10,
            gap=20,
            hdiag=f"$stem+{(n:=30)}",
            ldiag=f"$stem-{n}",
            sfw="$instem + $stem + $instem",
            nstem=f"$stem - {15}",
            ninstem=f"$instem - {30}",
            nsfw="$ninstem*2 + $nstem",
            nshoulder=-5,
            brackw=60,
            brackh=80,
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
    
    return DATPens([
        (single_char
            .glyph_view(r, glyph, None, Overlay.Info in rs.overlays)
            .translate(100, 300)),
        (single_char
            .test_string(0.15, glyph.name + (rs.read_text(clear=False) or "SPACING"))
            .translate(50, 50)).s(None).f(0.25)])