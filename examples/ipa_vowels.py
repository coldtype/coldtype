from coldtype import *

# https://brill.com/page/BrillFontDownloads/Download-The-Brill-Typeface

font = Font.Find("Brill-Bold")

@animation(bg=1)
def scratch(f:Frame):
    r = f.a.r.inset(100)
    
    close = P().m(r.pnw).l(r.pne).ep()
    open = P().m(open_front:=r.drop(0.55, "W").psw).l(r.pse).ep()
    front = P().m(r.pnw).l(open_front).ep()
    back = P().m(r.pne).l(r.pse).ep()
    central = P().m(r.pn).l(open.point_t(0.5)[0]).ep()

    def xbar(t):
        return P().m(front.point_t(t)[0]).l(back.point_t(t)[0]).ep()
    
    near_close = xbar(0.165)
    close_mid = xbar(0.33)
    mid = xbar(0.5)
    open_mid = xbar(0.66)
    near_open = xbar(0.66+0.165)

    lines = (P(close, open, front, back, central, close_mid, open_mid))
    
    def v(c, line, t):
        o = line.point_t(t)[0]
        p = StSt(c, font, 70).f(0).partition(lambda p: p.data("glyphCluster")).track(30)
        p.align(Rect.FromCenter(o, 1), tx=1).t(0, 7)
        return P(
            P().rect(p.ambit(tx=1, ty=1).inset(-20)).f(0.9).tag("knockout"),
            p.tag("symbols"))
    
    def vs(cs, line, ts=(0, 0.5, 1.0)):
        return P().enumerate(cs, lambda x: v(x.el, line, ts[x.i]))
    
    res = (P(
        vs(["iy", "ɨʉ", "ɯu"], close),
        vs(["ɪʏ", "ʊ"], near_close, [0.15, 0.85]),
        vs(["eø", "ɘɵ", "ɤo"], close_mid),
        vs(["e̞ø̞", "ə", "ɤ̞o̞"], mid),
        vs(["ɛœ", "ɜɞ", "ʌɔ"], open_mid),
        vs(["æ", "ɐ"], near_open),
        vs(["aɶ", "ä", "ɑɒ"], open)
        ))
    
    lines = lines.outline(1).difference(P(res.copy().find("knockout")))

    return (P(
        lines.f(hsl(0.75, 0.6, 0.85)),
        P(res.find("symbols")).f(hsl(0.65, 0.7, 0.40)),
    ))
