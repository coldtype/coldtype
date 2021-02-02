from coldtype.test import *

class glyphfn():
    def __init__(self):
        self.w = 1000
        self.r = Rect(w, 750)

    def __call__(self, func):
        self.func = func
        self.name = func.__name__
        return self


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
            gbƒ_gmƒgc="R$sfhb a $sfht",
            gxb="&gm/TY=$xbarh")
        return self
    
    def spaced_frame(self):
        if "empty" in self.guides:
            return self.getFrame().expand(self.l+self.r, "mxx")
        return self.bounds().expand(self.l+self.r, "mxx")
    
    setWidth = set_width
    
    def add_stem(self):
        return self.register(sl="TX-$stem/OX$instem")
    
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
            c = hsl(idx/2.3, 1, a=0.25)
            g = (DP(x)
                .translate(self.l, 0)
                .f(None)
                .s(c).sw(10))
            if k in ["gb", "gc", "gxb"]:
                c = hsl(0.6, 1, 0.5, 0.25)
                g.s(c).sw(2)
            dps += g
            dps += DATText(k, Style("Helvetica", 24, load_font=0, fill=c.with_alpha(0.5).darker(0.2)), Rect.FromCenter(g.bounds().pne, 100))
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
    def __init__(self, rect=(2000, 1200), feature="A"):
        self.glyphs = []
        for k, v in globals().items():
            if isinstance(v, glyphfn):
                self.glyphs.append(v)
        self.glyphs.sort(key=lambda a: a.name)
        super().__init__(rect, timeline=Timeline(len(self.glyphs), storyboard=[self.fn_to_frame(feature)]), rstate=1)

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
        .register(
            blƒ_ƒbr=f"TY-$sfhb/C$sfw-{(c:=20)} $gap $sfw+{c} a")
        .set_width(g.br.mxx)
        .guide(
            xb="&gxb/OY-&gxb.h*0.65",
            sl="&bl/TX=$ldiag",
            sr="&br/TX=$hdiag+10",
            apex="&bl⊣∩&gc⊥/OY-20",
            l1ƒl1o="&sl↗⨝&apex〻OX-&sl.w",
            l2ƒl2o="&sr↖⨝&apex〻OX+&sr.w")
        .ep("&l1⍺ &apex &l1∩&bx⊤ &l1o∩&bx⊤ &l1o⍺")
        .ep("&l2o⍺ &l2o∩&bx⊤ &l1o∩&bx⊤ &apex &l2⍺")
        .ep("""&xb⊤∩&l1/OX-10 &xb⊤∩&l2/OX+10
            &xb⊥∩&l2/OX+10 &xb⊥∩&l1/OX-10 R""")
        .brackets([
            (g.bl, ~g.l1o, "NW"),
            (g.br, ~g.l1, "NE"),
            (g.br, ~g.l2, "NW"),
            (g.br, ~g.l2o, "NE")]))

@glyphfn()
def I(r, g):
    return (g
        .set_width(g.c.stem*3)
        .register(bm=g.gb, cm=g.gc, sm="TX=$stem")
        .brackets([
            (g.cm, g.sm, "S"),
            (g.bm, g.sm, "N")]))

@glyphfn()
def J(r, g):
    return (g
        .setWidth(g.c.stem*4.25)
        .guide(
            eblƒkyƒsrƒrght="C $stem+20 a $stem $instem",
            ebl="&ebl/MY+&gxb.mdy",
            ky="&ky/EY-$over")
        .register(
            sr="&sr/MY-&gxb.mny",
            cr="&gc/MX-&ky.mnx")
        .guide(iky="&ky/SY-&gb.h")
        .constants(ic=85, oc=75)
        .ep("""&sr/MY-&ebl.mxy↙ ↘|$ic|&iky↓
            ↙|$ic|&ebl↗ #↖ ↙|$oc|&ky↓ ↘|$oc-8|&sr↘""")
        .brackets([(g.cr, g.sr, "S")]))

@glyphfn()
def H(r, g):
    return (g
        .register(
            blƒ_ƒbr=f"&gb/C $sfw $gap $sfw a",
            clƒ_ƒcr=f"&gc/C $sfw $gap $sfw a",
            sl="TX-$stem/MX=&bl.ps.x",
            sr="TX-$stem/MX=&br.ps.x",
            xb="&gxb/OY-10/MX-&bl.pc.x/MX+&br.pc.x")
        .set_width(g.br.mxx)
        .brackets([
            (g.cl, g.sl, "S"),
            (g.cr, g.sr, "S"),
            (g.bl, g.sl, "N"),
            (g.br, g.sr, "N")]))

@glyphfn()
def K(r, g):
    return (g
        .declare(rn:=10)
        .register(
            blƒ_ƒbr=f"&gb/C $sfw-{rn} $gap $sfw+{rn} a",
            clƒ_ƒcr=f"&gc/C $sfw-{rn} $gap $sfw+{rn} a",
            sl="TX-$stem/MX=&bl.ps.x")
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
            bl=g.gb, cl=g.gc,
            earbƒ_centerƒeart="TX+$stem/R $earhb-30 a $earht-20",
            xbar="&gxb/MX-&sl.pc.x/MX+&eart.psw.x-50")
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.bl, g.sl, "NW")]))

@glyphfn()
def F(r, g):
    return (E.func(r, g)
        .remove("earb")
        .constants(sy=20)
        .register(
            eart="&eart/EY-$sy",
            xbar="&xbar/OY-$sy",
            bl="&bl/MX+&xbar.mxx+$sy*0.5")
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.bl, g.sl, "N"),
            (g.cl, g.eart, "SW", 100, 100, 0.8)]))

@glyphfn()
def L(r, g):
    return (g
        .set_width(g.c.stem*4.25)
        .add_stem()
        .register(
            bl=g.gb,
            cl="&gc/TX-$sfw",
            earb="+$stem -$earhb*1.1")
        .brackets([
            (g.cl, g.sl, "S"),
            (g.bl, g.sl, "NW"),
            (g.bl, g.earb, "NW", 140, 130, 0.95)]))

@glyphfn()
def Z(r, g:Glyph):
    diag = g.c.ldiag + 30
    return (g
        .constants(dw=g.c.ldiag + 50)
        .set_width(g.c.stem*4.5)
        .guide(
            gc="&gc/SX-30",
            hdrƒhdl="&bx↗⨝&bx↙OX+$dw〻OX-$dw")
        .register(
            eart=f"T-$stem +$earht/OX&gc.mnx",
            earb="+$stem -$earhb")
        .ep("&hdl &hdr~")
        .ep("&gc↖↙ &gc⊥∩&hdr/OX-50 &gc⊤∩&hdr/OX-50")
        .ep("&gb↘↗ &gb⊤∩&hdl/OX+50 &gb⊥∩&hdl/OX+50")
        .brackets([
            (g.gc, g.eart, "SE", 200, 80, 0.85),
            (g.gb, g.earb, "NW", 200, 80, 0.85)]))

@glyphfn()
def T(r, g):
    return (g
        .set_width(g.c.stem*4.75)
        .register(
            bm="&gb/TX=$sfw",
            cm="&gc",
            earl="-$stem +$earht+20",
            earr="+$stem +$earht+20",
            sm="TX=$stem")
        .brackets([
            (g.cm, g.earl, "SE", 100, 100, 0.95),
            (g.cm, g.earr, "SW", 100, 100, 0.95),
            (g.bm, g.sm, "N")]))

def _P(g, ci=30, my=0, mn=0):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .guide(
            sr=f"TX +$stem+{ci}",
            center="&gxb/OY-30",
            bxc=f"SY-&center.mny+{mn}",
            _crv="&bxc/MX-&sl.mxx+50",
            _midƒkxƒ_cl=f"&bxc/R {mh} a $sfht",
            kx=f"&kx/MX+&sr.mnx",
            _mid="&mid/MX-&sl.pc.x/MX+&crv.mnx",
            cl="&cl/MX+&crv.mnx"))

@glyphfn()
def P(r, g, mod=None, ci=30, my=0, mn=0):
    mh = g.c.xbarh + my
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .guide(
            _sr=f"TX +$stem+{ci}",
            gxb="&gxb/OY-30",
            _crvt=f"SY-&gxb.mny",
            _crv="&crvt/MX-&sl.mxx+50",
            _midƒ_kxƒ_cl=f"&crvt/R {mh} a $sfht",
            _kx=f"&kx/MX+&sr.mnx",
            mid="&mid/MX-&sl.pc.x/MX+&crv.mnx",
            _cl="&cl/MX+&crv.mnx")
        .register(bl="&gb/MX+&sr.mnx-$gap")
        .chain(mod)
        .constants(ci=0.9, co=0.65)
        .ep("&cl↖↙↘ ↗|$ci|&kx→ ↘|$ci|&mid↗ &mid↖↙↘ ↘|$co|&crv→ ↗|$co|&cl↗",
            tag="curve")
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.bl, g.sl, "N")]))

@glyphfn()
def B(r, g):
    return (P.func(r, g, my=-10, mn=30, mod=λg: (g
        .register(bl=g.bl.take(g.cl.w, "mnx"))))
        .remove("curve")
        .guide(
            _bbxc=f"M-&crv.mnx +&kx.mny/EX+{(bnx:=10)}",
            _bkx=f"&bbxc/M+&kx.mxx+{bnx*1} -&bl.mxy/MY+&mid.mny")
        .ep("""&cl↖↙↘ ↗|$ci|&kx→ ↘|$ci|&mid↗ &mid↖↙ #↙OX+20/OY+10
            ↘|$co|&crv→ ↗|$co|&cl↗""")
        .ep("""&mid↙↘ ↗|$ci|&bkx→ ↘|$ci|#↙ &bl↖↙
            #↘OX+20 ↘|$co|&bbxc→OX+30 ↗|$co|&mid↗OX-50/OY-10""")
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.bl, g.sl, "NW")]))

@glyphfn()
def R(r, g):
    return (P.func(r, g, ci=50, mn=30, mod=λg: g
        .guide(br="+$sfw -$sfhb/OX60/MX-&sr.mnx")
        .ep("""&mid↘OX-30 ↗|65|&br↖ ↙|75|&sr↘OX-20 &br↘↗
            &sr/MY-&br.mxy↘OX-10 ↗|70|&mid↘OX50/OY20""")))

@glyphfn()
def D(r, g):
    return (g
        .set_width(g.c.stem*4.5)
        .add_stem()
        .guide(
            sr="TX+$stem+30",
            Ƨkx="&gm/MX-&sl.mxx+20/MX+&sr.mnx",
            kbƒ_ƒkt="&kx/R a $xbarh+-10 a")
        .constants(ic=75, oc=65)
        .ep("""&gc↖↙ &kt↖ ↗|$ic|#↘ &kb↗ ↘|$ic|#↙ &gb↖↙
            &sl↘ ↘|$oc|&sr→ &gxb↗/OY-20 ↗|$oc|&sl↗""")
        .brackets([
            (g.gc, g.sl, "SW"),
            (g.gb, g.sl, "NW")]))

@glyphfn()
def N(r, g):
    return (g
        .set_width(int(g.c.stem*5.25))
        .register(
            _ƒslƒ_ƒsr="C $ninstem $nstem a $nstem $ninstem",
            bl="-$nsfw -$sfhb",
            clƒ_ƒcr="&gc/C $nsfw a $nsfw",
            cl="&cl/MX+&sl.mxx")
        .guide(
            l1=Line((g.sl.ee & g.cl.es)//-30, g.bl.pne/30),
            l2=λg: g.l1.offset(min(g.c.hdiag+40, g.cr.psw.x-g.l1[0].x-g.c.gap), 0))
        .ap(DP("diag2")
            .mt(g.l1 & g.sl.ee, g.l1 & g.bx.es, g.sr.ps)
            .lt(g.l2 & g.sr.ecx, g.l2 & g.bx.en, g.cl.pn).cp())
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.cr, g.sr, "S"),
            (g.bl, g.sl, "N")]))

@glyphfn()
def M(r, g):
    return (g
        .set_width(g.c.stem*6.25)
        .declare(wght:=g.c.hdiag-15)
        .guide(
            gcaplƒ_ƒgcapr="&gc/C $nsfw a $nsfw",
            base=g.gb)
        .register(
            _ƒslƒ_ƒsr="C $ninstem $nstem a $nstem $ninstem",
            blƒ_ƒbr="&gb/C $nsfw a $nsfw",
            cl="&gcapl/MX+&sl.mxx",
            cr="&gcapr/MX-&sr.mnx")
        .guide(
            l1=Line((g.cl.es & g.sl.ee)//(n:=-60), g.bl.pne/g.c.gap),
            l1o=λ.l1.offset(wght, 0),
            l2=Line((g.cr.es & g.sr.ew)//n, g.br.pnw/-g.c.gap),
            l2o=λ.l2.offset(-wght, 0))
        .ap(DP("dl")
            .mt(g.l1 & g.bx.en, g.l1 & g.bx.es)
            .lt(g.l2 & g.bx.es, g.l2 & g.bx.en)
            .lt(g.l2o & g.bx.en, g.l2o & g.gb.en)
            .lt(g.l1o & g.gb.en)
            .lt(g.l1o & g.bx.en))
        .brackets([
            (g.cl, g.sl, "SW"),
            (g.bl, g.sl, "N"),
            (g.cr, g.sr, "SE"),
            (g.br, g.sr, "N")]))

@glyphfn()
def O(r, g, clx=0):
    (g.set_width(g.c.stem*4.15)
        .space(n:=g.l+5, n)
        .constants(
            hw=g.c.stem+35,
            oc=65,
            ic=85)
        .guide(
            slƒkyƒsr="IY-$over/C $hw a $hw",
            o="IY-$over",
            i="&ky/MY+&gc.mny/MY-&gb.mxy",
            ox="&gxb/IY20",
            ix=λg: g.gxb.sect(g.ky)))
    
    return (g
        .ep("&ox↗ ↗|$oc|&o↑ ↖|$oc|&ox↖ &ox↙ ↙|$oc|&o↓ ↘|$oc|&ox↘")
        .ep("&ix↗ ↗|$ic|&i↑ ↖|$ic|&ix↖ &ix↙ ↙|$ic|&i↓ ↘|$ic|&ix↘ R"))

@glyphfn()
def Q(r, g):
    return (O.func(r, g)
        .guide(quill="T=$stem -$sfhb/OY-$sfhb*0.5/MX=&i.mxx")
        .ap(DP(g.quill).rotate(23)))

@glyphfn()
def C(r, g, pullup=None):
    return (g
        .set_width(g.c.stem*4)
        .guide(
            Ƨstemlƒcntryƒstemr="IY-$over/C $stem+30 a $stem-10",
            sr="&stemr/TX-0.5",
            cy="&cntry",
            kbƒixbarƒkt="&cntry/SY-$sfhb/SY+$sfht/Ra $xbarh a",
            ox="&gxb/IY+25/MX+&sr.mxx",
            ix="&ixbar/IY+10",
            Ƨxbar="&ixbar/OY-$gap*2/MX-&kb.pc.x-20/MX+&stemr.mxx")
        .register(
            eart="&stemr/MY-&ixbar.mxy/MY+&bx.mxy")
        .constants(oc=71, ic=85)
        .ep(f"""&kt↘OX&sr.w &sr↗|$oc-8|&cy↑OX-25
            ↖|$oc|&ox↖ #↙ ↙|$oc|&cy↓OX-10 {pullup or "↘|$oc|&gxb↘"}
            &kb↗ &kb↘OX-10|$ic-5|&kb↓OX-5
            ↙|$ic|&ix↙ &ix↖ ↖|$ic|&kt↑ &kt↗OX-7|$ic-5|&kt↘"""))

@glyphfn()
def G(r, g):
    return (C.func(r, g, pullup="↘|$oc|&xbar↗")
        .ep("&xbar↗↖↙ #/MX+&sr.mxx↘"))

@glyphfn()
def S(r, g):
    return (g
        .set_width(g.c.stem*4.15)
        .register(
            earb="T-$stem -$earhb-20",
            eart="T+$stem +$earht-10")
        .guide(
            tbx="TY+&eart.h/OY-40",
            bbx="TY-&earb.h",
            _bxy="I+$hdiag -$over",
            bxi="I+$hdiag $over*0.75/SY-$sfhb/SY+$sfht/OX15/I10 -30/EY-40",
            kbƒ_ƒkt="&bxi/R a $xbarh-20 a"
            )
        .constants(stx=30, sty=50, smx=25)
        .ep("""&eart↓ ↗|65|&bxy↑/OX-$stx ↖|65|&tbx←
            -&kb↖ ↙↗|62,40|&kb↘/OY+$sty ↘|65|&kb↓/OX+$smx &bxi↙|65|&earb↗
            &earb↑ ↙|65|&bxy↓/OX$stx*2 ↘|65|&bbx→/OX20
            -&kt↘ ↗↙|62,40|&kt↖/OY-$sty ↖|65|&kt↑/OX-$smx/OY5 &bxi↗|65|&eart↙"""))

@glyphfn()
def U(r, g):
    c = 90
    return (g
        .register(
            clƒ_ƒcr="1 +$sfht/C $sfw $gap*2 $sfw-70 a")
        .set_width(g.cr.mxx)
        .register(
            sl=f"TX-$hdiag+0/M =&cl.ps.x -$sfhb+{c}",
            sr=f"TX+$ldiag+20/M =&cr.ps.x -$sfhb+{c}")
        .guide(
            cy="MX-&sl.mxx/MY--$over/MX+&sr.mnx",
            ky="&cy/MY-$sfhb")
        .constants(oc=75, ic=90)
        .ep("&sl↙ ↙|$oc|&cy↓ ↘|$oc|&sr↘ &sr↙ ↘|$ic|&ky↓ ↙|$ic|&sl↘",
            tag="curve")
        .brackets([
            (g.cl, g.sl, "S"),
            (g.cr, g.sr, "S")]))

@glyphfn()
def V(r, g):
    return (U.func(r, g)
        .remove("sl", "sr", "curve").brackets([])
        .guide(
            apex="&ky↓/O 4 20",
            l1="&sl⊣∩&cl⊥⨝&apex",
            l2="&sr⊢∩&cr⊥⨝&apex",
            l1o="&l1/OX-&sl.w",
            l2o="&l2/OX+&sr.w")
        .ep("""&l1⍺ &l1/↕0.1⍵ &l2/↕0.1⍵ &l2⍺ &l2o⍺
            &l2o∩&bx⊥ &l1o∩&bx⊥ &l1o⍺ R""")
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
            "&gc/C $sfw $gap $sfw-30 $gap $sfw-40 a")
        .set_width(g.cr.mxx)
        .guide(
            csl=g.cl.t(0, g.c.ldiag+50),
            csm=g.cm.t(0, g.c.ldiag+10),
            csr=g.cr.t(0, g.c.ldiag+10),
            blƒ_ƒbr="&gb/EY+30/MX-&cl.mdx/MX+&cr.mdx/IX30/OX10/Caƒ$gapƒa")
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
            blƒ_ƒbr=f"&gb/C$sfw-{(f:=20)} $gap $sfw+{f} a",
            clƒ_ƒcr=f"&gc/C$sfw+{f} $gap $sfw-{f} a")
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
        #.add_stem()
        .constants(hd=g.c.hdiag+15)
        .register(
            clƒ_ƒcr=f"&gc/C $sfw+{(f:=50)} $gap $sfw-{f} a",
            bc="&gb/MX-&cl.pc.x-10/MX+&cr.pc.x+10",
            sc="T=$hd -0.45/MX=&bc.pc.x")
        .ap(hd:=DP().lsdiagc(g.cl.t(0, g.c.hd).es, g.sc.en, g.sc.ee, extr=0.1))
        .ap(ld:=DP().lsdiag(g.cr.t(0, g.c.ldiag).es, g.sc.t(1, g.c.ldiag).en, extr=0.1))
        .brackets([
            (g.bc, g.sc, "N"),
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

@font((2000, 1500), feature="Z")
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
    
    char = chr(glyph_to_uni(glyph.name))
    
    return DATPens([
        (single_char
            .glyph_view(r, glyph, None, Overlay.Info not in rs.overlays)
            .translate(100, 300)
            .append(λdps: dps.fft("cutout").copy().f(1).s(None).translate(0, 600).phototype(r, blur=7, cutw=10, fill=bw(0)).img_opacity(0.05))),
        (single_char
            .test_string(0.15, rs.read_text(clear=False) or ("OH" + char + "NO"))
            .translate(50, 50)).s(None).f(0.25)
        ]
        )