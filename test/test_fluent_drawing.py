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
        self.guide(
            gbƒ_gmƒgc="r $sfhb a $sfht",
            gxb="&gm ^t 1 =$xbarh")
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
            g = (DP(x)
                .translate(self.l, 0)
                .f(None)
                .s(hsl(idx/2.3, 1, a=0.25)).sw(10))
            if k in ["gb", "gc", "gxb"]:
                g.s(hsl(0.6, 1, 0.5, 0.25)).sw(2)
            dps += g
        return dps

    def brack(self, a, b, pt, y=None, x=None, c=None):
        if not x:
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

            self.brack(a, b, pt[0])
            self.brack(a, b, pt[1])
            return self

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
                .tag("cutout")),
            lpts if overlay else None,
            (build_glyph(
                single_char.glyphs[single_char.char_to_frame(compare)])
                .scale(0.75, center=Point([0, 0]))
                .translate(glyph.spaced_frame().w+30, 0)
                .pen()
                .removeOverlap()
                .f(hsl(0.9, a=0.25))
                .s(None)) if compare else None])
    
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


@glyphfn()
def A(r, g):
    return (g
        .register(blƒ_ƒbr=f"1 -$sfhb ^c $sfw-{(c:=20)} $gap $sfw+{c} a")
        .set_width(g.br.mxx)
        .guide(
            Ƨxbar="&gxb ^o 0 -&gxb.h*0.65",
            Ƨsteml=f"&bl ^t =$ldiag 1",
            Ƨstemr=f"&br ^t =$hdiag+10 1",
            apex=λg: g.gc.ps * g.bl.pne.x // -20,
            Ƨl1=λg: Line(g.steml.pne, g.apex),
            Ƨl2=λg: Line(g.stemr.pnw, g.apex),
            Ƨl1o=λg: g.l1 / -g.steml.w,
            Ƨl2o=λg: g.l2 / g.stemr.w)
        .ap(DP("l").mt(g.l1.start)
            .lt(g.apex, g.l1 & g.bx.en, g.l1o & g.bx.en, g.l1o.start).cp())
        .ap(DP("r").mt(g.l2o.start)
            .lt(g.l2o & g.bx.en, g.l1o & g.bx.en, g.apex, g.l2.start).cp())
        .ap(DP().rect(g.xbar).ƒ(g.l1/-30, ~g.l2/30))
        .brackets([
            (g.bl, ~g.l1o, "NW"),
            (g.br, ~g.l1, "NE"),
            (g.br, ~g.l2, "NW"),
            (g.br, ~g.l2o, "NE")]))

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
        .register(
            earƒknckƒsrƒrght="c $stem+20 a $stem $instem",
            ear="&ear ^m ø +&gxb.mdy",
            sr="&sr ^m ø -&gxb.mny",
            knck="&knck ^e 0 -$over",
            cr="&gc ^m -&knck.mnx ø")
        .remove("knck", "rght")
        .guide(iknck="&knck ^s 0 -&gb.h")
        .ap(DP()
            .mt(g.sr.psw // 60)
            .bct(g.iknck.ps, "SE", ic:=0.85)
            .bct(g.ear.pne, "SW", ic+0.03)
            .lt(g.ear.pnw)
            .bct(g.knck.ps, "SW", oc:=0.75)
            .bct(g.sr.pse, "SE", oc-0.08)
            .cp())
        .remove("ear")
        .brackets([(g.cr, g.sr, "S")]))

@glyphfn()
def H(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"&gb ^c $sfw $gap $sfw a",
            clƒ_ƒcr=f"&gc ^c $sfw $gap $sfw a",
            steml="-$stem 1 ^m =&bl.ps.x ø",
            stemr="-$stem 1 ^m =&br.ps.x ø")
        .set_width(g.br.mxx)
        .ap(DP(g.gxb//-10).ƒ(g.steml.ecx, ~g.stemr.ecx))
        .brackets([
            (g.cl, g.steml, "S"),
            (g.cr, g.stemr, "S"),
            (g.bl, g.steml, "N"),
            (g.br, g.stemr, "N")]))

@glyphfn()
def K(r, g):
    return (g
        .declare(rn:=10)
        .register(
            blƒ_ƒbr=f"&gb ^c $sfw-{rn} $gap $sfw+{rn} a",
            clƒ_ƒcr=f"&gc ^c $sfw-{rn} $gap $sfw+{rn} a",
            sl="-$stem 1 ^m =&bl.ps.x ø")
        .ap(ld:=DP().lsdiagc(g.cr.t(0, ldw:=g.c.ldiag+30).es,
            g.bl.t(0, ldw).en@(g.gxb.mny-50),
            g.sl.ecx, extr=0.1))
        .ap(hd:=~DP().lsdiagc(g.br.t(0, hdw:=g.c.hdiag-10).en,
            g.cl.t(0, hdw).es,
            ld.sl(0)//-50, extr=0.1))
        .brackets([
            (g.cl, g.sl, "S"),
            (g.bl, g.sl, "N"),
            (g.cr, ld.sl(2), "SE"),
            (g.cr, ~ld.sl(0), "SW"),
            (g.br, hd.sl(3), "NW"),
            (g.br, ~hd.sl(1), "NE")
            ]))

@glyphfn()
def E(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .register(
            base=g.gb, cap=g.gc,
            earbƒ_centerƒeart="+$stem 1 ^r $earhb-20 a $earht-20",
            earb="&earb ^o 0 0",
            xbar="&center ^m -&stem.pc.x ø ^m +&eart.psw.x-40 ø ^t 1 =$xbarh")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "NW"),
            (g.cap, g.eart, "SW", 200, 80, 0.85),
            (g.base, g.earb, "NW", 200, 80, 0.85)
            ]))

@glyphfn()
def F(r, g):
    return (E.func(r, g)
        .remove("earb")
        .register(
            xbar="&xbar ^o 0 -20",
            base="&base ^m +&xbar.mxx+10 ø")
        .brackets([
            (g.cap, g.stem, "SW"),
            (g.base, g.stem, "N"),
            (g.cap, g.eart, "SW", 200, 100, 0.8)]))

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
            (g.base, g.stem, "NW"),
            (g.base, g.earb, "NW", 200, 80, 0.85)]))

@glyphfn()
def Z(r, g:Glyph):
    diag = g.c.ldiag + 30
    return (g
        .set_width(g.c.stem*4.5)
        .register(
            cap=f"1 +$sfht ^s -{(xti:=30)} 0",
            eart=f"-$stem +$earht ^o {xti} 0",
            base="1 -$sfhb",
            earb="+$stem -$earhb")
        .ap(hd:=DP().lsdiag(g.bx.pne/-g.c.hdiag | g.bx.pne, g.bx.psw | g.bx.psw/g.c.hdiag))
        .guide(hdlm=hd.sl(0).i(0.5, ~hd.sl(2)))
        .ap(DP().lsdiagc(g.cap.ew, g.cap.ee, g.hdlm))
        .ap(~DP().lsdiagc(g.base.ee, g.base.ew, g.hdlm))
        .remove("cap", "base")
        .brackets([
            (g.cap, g.eart, "SE", 200, 80, 0.85),
            (g.base, g.earb, "NW", 200, 80, 0.85)]))

@glyphfn()
def T(r, g):
    return (g
        .set_width(g.c.stem*4.75)
        .register(
            base="=$sfw -$sfhb",
            cap="1 +$sfht",
            earl="-$stem +$earht+20",
            earr="+$stem +$earht+20",
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
            center="&gxb ^o 0 -30",
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
    return (P.func(r, g, my=-10, mn=20, xc=0, mod=λg: (g
        .register(
            base=g.base.take(g.cap.w, "mnx")))
        .guide(
            _bbxc=f"1 1 ^m -&curve.mnx +&knock.mny ^e +{(bnx:=10)} 0",
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
            Ƨblƒgapƒcl="r $sfhb a $sfht",
            stemr="+$stem+30 1",
            Ƨknck="&gap ^m -&stem.mxx+20 ø ^m +&stemr.mnx ø",
            knckbƒ_ƒknckt="&knck ^r a $xbarh+-10 a")
        .ap(DP("curve")
            .mt(g.cl.psw)
            .lt(g.knckt.pnw)
            .bct(g.knckt.pse, "NE", (ic:=0.75))
            .lt(g.knckb.pne)
            .bct(g.knckb.psw, "SE", ic)
            .lt(g.bl.pnw, g.bl.psw, g.stem.pse)
            .bct(g.stemr.pe @ (g.knckb.pne.y+(n:=10)), "SE", (oc:=0.65))
            .lt(g.stemr.pe @ (g.knckt.pse.y-n))
            .bct(g.stem.pne, "NE", oc)
            .lt(g.cl.pnw)
            .cp())
        .brackets([
            (g.cl, g.stem, "SW"),
            (g.bl, g.stem, "NW")]))

@glyphfn()
def R(r, g):
    return (P.func(r, g, mn=30, mod=λg: g
        .register(base=g.base.subtract(20, "mxx"))
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
            .cp())))

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
            l1=Line((g.steml.ee & g.capl.es)//-30, g.base.pne/30),
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
        .set_width(g.c.stem*6.25)
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
            .mt(r.pe@g.gxb.pe.y//off)
            .bct(r.pn, "NE", offc)
            .bct(r.pw@g.gxb.pw.y//off, "NW", offc)
            .lt(r.pw@g.gxb.pw.y//-off)
            .bct(r.ps, "SW", offc)
            .bct(r.pe@g.gxb.pe.y//-off, "SE", offc)
            .cp())
    
    return (g
        .ap(o(g.o, 30, 0.65).tag("O"))
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
            Ƨstemlƒcntryƒstemr="i 0 -$over ^c $stem+30 a $stem-10",
            knckbƒixbarƒknckt="&cntry ^s 0 -$sfhb ^s 0 +$sfht ^r a $xbarh a")
        .register(
            eart="&stemr ^m ø -&ixbar.mxy ^m ø +&bx.mxy")
        .ap(DP("curve")
            .mt(g.gxb.pne/(-g.stemr.w/2))
            .bct(g.cntry.pn/-20, "NE", (oc:=0.71))
            .bct(g.gxb.pnw//-(n:=30), "NW", oc)
            .lt(g.gxb.psw//n)
            .bct(g.cntry.ps/-10, "SW", oc)
            .bct(g.gxb.pse, "SE", oc)
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
            .bct(g.bxi.ps/(smallx:=15)//-20, "SE", small:=0.65)
            .bct(g.earb.pne, g.bxi.psw//-20, land:=0.65)
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
            clƒ_ƒcr="1 +$sfht ^c $sfw $gap*2 $sfw-70 a")
        .set_width(g.cr.mxx)
        .register(
            steml=f"-$hdiag+0 1 ^m =&cl.ps.x -$sfhb+{c}",
            stemr=f"+$ldiag+20 1 ^m =&cr.ps.x -$sfhb+{c}")
        .guide(
            center="m -&steml.mxx --$over ^m +&stemr.mnx ø",
            knock="&center ^m ø -$sfhb")
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
            (g.cl, g.steml, "S"),
            (g.cr, g.stemr, "S")]))

@glyphfn()
def V(r, g):
    return (U.func(r, g)
        .remove("steml", "stemr", "curve")
        .guide(
            center="&center ^m ø -0",
            apex=g.knock.ps//20/0,
            l1=λg:Line(g.steml.ee & g.cl.es, g.apex),
            l2=λg:Line(g.stemr.ew & g.cr.es, g.apex),
            l1o=λg:g.l1/-g.steml.w,
            l2o=λg:g.l2/g.stemr.w)
        .ap(v:=~DP().mt(g.l1.start)
            .lt(g.l1.extr(0.1).end) # could limit based on l2o?
            .lt(g.l2.extr(0.1).end) # could limit based on l1o?
            .lt(g.l2.start)
            .lt(g.l2o.start)
            .lt(g.l2o & g.bx.es)
            .lt(g.l1o & g.bx.es)
            .lt(g.l1o.start)
            .cp())
        .brackets([
            (g.cl, ~g.l1o, "SW"),
            (g.cl, ~g.l1, "SE"),
            (g.cr, ~g.l2, "SW"),
            (g.cr, ~g.l2o, "SE")]))

@glyphfn()
def W(r, g):
    return (g
        .constants(sfw=g.c.sfw+-50)
        .register(clƒ_ƒcmƒ_ƒcr=
            "1 +$sfht ^c $sfw $gap $sfw-30 $gap $sfw-40 a")
        .set_width(g.cr.mxx)
        .guide(
            csl=g.cl.t(0, g.c.ldiag+50),
            csm=g.cm.t(0, g.c.ldiag+10),
            csr=g.cr.t(0, g.c.ldiag+10),
            blƒ_ƒbr="1 -$sfhb+30 ^m -&cl.mdx ø ^m +&cr.mdx ø ^i 30 0 ^o 10 0 ^c a $gap a")
        .guide(
            l1=Line(g.csl.pse, a1:=g.bl.pn),
            l2=Line(g.csm.psw, a1),
            l3=Line(g.csm.pse, a2:=g.br.pn),
            l4=Line(g.csr.psw, a2))
        .guide(
            l1o=g.l1/-g.csl.w,
            l2o=g.l2/g.csm.w,
            l3o=g.l3/-g.csm.w/-30,
            l4o=g.l4/g.csr.w)
        .ap(~DP("vv")
            .mt(g.l1.start)
            .lt(g.l1.extr(0.1).end)
            .lt(g.l2.extr(0.1).end)
            .lt(g.l2.start)
            .lt(g.l3.start)
            .lt(g.l3.extr(0.1).end)
            .lt(g.l4.extr(0.1).end)
            .lt(g.l4.start)
            .lt(g.l4o.start)
            .lt(g.l4o & g.bx.es)
            .lt(g.l3o & g.bx.es)
            .lt(Line(g.l3o.end, g.l3o & g.l2o).extr(0.1).end)
            .lt(Line(g.l2o.end, g.l2o & g.l3o).extr(0.1).end)
            .lt(g.l2o & g.bx.es)
            .lt(g.l1o & g.bx.es)
            .lt(g.l1o.start)
            .cp())
        .brackets([
            (g.cl, ~g.l1o, "SW"),
            (g.cl, ~g.l1, "SE"),
            (g.cm, ~g.l2, "SW"),
            (g.cm, ~g.l3, "SE"),
            (g.cr, ~g.l4, "SW"),
            (g.cr, ~g.l4o, "SE")
        ]))

@glyphfn()
def X(r, g):
    return (g
        .declare(
            ox:=40,
            hdw:=g.c.hdiag+20,
            ldw:=g.c.ldiag+20)
        .register(
            blƒ_ƒbr=f"1 -$sfhb ^c $sfw-{(f:=20)} $gap $sfw+{f} a",
            clƒ_ƒcr=f"1 +$sfht ^c $sfw+{f} $gap $sfw-{f} a")
        .set_width(g.br.mxx)
        .ap(hd:=DP()
            .lsdiag(g.cl.t(0, hdw).es, g.br.t(0, hdw).en, extr=0.1))
        .guide(hdlm=hd.sl(0).i(0.5, ~hd.sl(2)))
        .ap(ldl:=~DP()
            .lsdiagc(g.bl.t(0, ldw).en,
                g.cr.t(0, ldw).o(-ox, 0).es, g.hdlm, extr=0.1))
        .ap(ldr:=DP()
            .lsdiagc(g.cr.t(0, ldw).es,
                g.bl.t(0, ldw).o(ox, 0).en, g.hdlm, extr=0.1))
        .brackets([
            (g.cl, ~hd.sl(0), "SW"),
            (g.cl, hd.sl(2), "SE"),
            (g.bl, ldl.sl(3), "NW"),
            (g.bl, ~ldl.sl(1), "NE"),
            (g.cr, ~ldr.sl(0), "SW"),
            (g.cr, ldr.sl(2), "SE"),
            (g.br, hd.sl(0), "NW"),
            (g.br, ~hd.sl(2), "NE")
            ]))

@glyphfn()
def Y(r, g):
    return (g
        .add_stem()
        .constants(hd=g.c.hdiag+15)
        .register(
            clƒ_ƒcr=f"1 +$sfht ^c $sfw+{(f:=50)} $gap $sfw-{f} a",
            base="1 -$sfhb ^m -&cl.pc.x-10 ø ^m +&cr.pc.x+10 ø",
            stem="&stem ^t =$hd -0.45 ^m =&base.pc.x ø")
        .ap(hd:=DP().lsdiagc(g.cl.t(0, g.c.hd).es, g.stem.en, g.stem.ee, extr=0.1))
        .ap(ld:=DP().lsdiag(g.cr.t(0, g.c.ldiag).es, g.stem.t(1, g.c.ldiag).en, extr=0.1))
        .brackets([
            (g.base, g.stem, "N"),
            (g.cl, ~hd.sl(0), "SW"),
            (g.cr, ld.sl(2), "SE")]))

@glyphfn()
def space(r, g):
    return (g
        .set_width(g.c.stem*2)
        .space(0, 0)
        .guide(empty=g.bx))

def build_glyph(cap):
    g = (Glyph()
        .addFrame(cap.r)
        .space(n:=10, n)
        .glyph_name(cap.func.__name__)
        .constants(
            _sfh=170,
            sfhb=λ.c._sfh+60,
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
            brackw=50,
            brackh=50,
            brackc=0.85)
        .set_width(cap.r.w))

    glyph = (cap.func(Rect(1080, 1080), g)
        .realize()
        .f(None)
        .s(0)
        .sw(2))
    
    return glyph

@font((2000, 1500))
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
            .translate(100, 300)
            .append(λdps: dps.fft("cutout").copy().f(1).s(None).translate(0, 600).phototype(r, blur=7, cutw=10, fill=bw(0)).img_opacity(0.05))),
        (single_char
            .test_string(0.15, rs.read_text(clear=False) or ("OH" + glyph.name + "NO"))
            .translate(50, 50)).s(None).f(0.25)])