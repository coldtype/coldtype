from coldtype import *

font = Font.Find("Brill-Bold")

vowels = """
iy  ɨʉ  ɯu
 ɪʏ    ʊ
eø  ɘɵ  ɤo
e̞ø̞  ə   ɤ̞o̞
ɛœ  ɜɞ  ʌɔ
æ   ɐ
aɶ  ä   ɑɒ
"""

@animation(bg=1)
def scratch(f:Frame):
    r = f.a.r.inset(100)
    
    close = P().m(r.pnw).l(r.pne).ep()
    open = P().m(open_front:=r.drop(0.5, "W").psw).l(r.pse).ep()
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
        p = StSt(c, font, 70).f(0)
        return P(
            p.align(Rect.FromCenter(o, 1)).tag("symbols").t(0, 7),
            P().rect(p.ambit(ty=1).inset(-20)).f(-1).tag("knockout"))
    
    def vs(cs, line, ts=(0, 0.5, 1.0)):
        return P().enumerate(cs, lambda x: v(x.el, line, ts[x.i]))
    
    res = (P(
        vs(["iy", "ɨʉ", "ɯu"], close),
        vs(["ɪʏ", "ʊ"], near_close, [0.15, 0.85]),
        vs(["eø", "ɘɵ", "ɤo"], close_mid),
        vs(["e̞ø̞", "ə", "ɤ̞o̞"], mid),
        vs(["ɛœ", "ɜɞ", "ʌɔ"], open_mid),
        vs(["æ", "ɐ"], near_open),
        vs(["aɶ", "ä", "ɑɒ"], open)))
    
    lines = lines.outline(1).difference(P(res.copy().find("knockout")))

    return (P(
        lines.f(hsl(0.75, 0.6, 0.85)),
        P(res.find("symbols")).f(hsl(0.65, 0.7, 0.40)),
    ))
