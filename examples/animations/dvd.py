from coldtype import *

font, fontSize = Font.MutatorSans(), 100
#font, fontSize = "OhnoFatfaceV", 200

border = Rect(500, 250)
speed = 5

@animation(tl=Timeline(300, 48)
    , memory=dict(x=250, y=250, c=0, xs=speed, ys=speed)
    , bg=0)
def scratch(f, m):
    r = f.a.r.inset(10)

    m.x += m.xs
    m.y += m.ys

    if m.x <= r.x or (r.x + m.x + border.w) >= f.a.r.mxx:
        m.xs = -m.xs
        m.c += random()*0.35

    if m.y <= r.y or (r.y + m.y + border.h >= f.a.r.mxy):
        m.ys = -m.ys
        m.c += random()*0.35
    
    a, b = (r.drop(border.w, "E")
        .drop(border.h, "N")
        .ipos(Point(m.x, m.y)))
    
    c = hsl(m.c, 1, 0.8)

    return P(
        P().oval(border).t(m.x, m.y).fssw(-1, c, 10),
        (StSt("DVD", font, fontSize
            , fvar_1=a
            , fvar_0=b)
            .f(c)
            .align(border.offset(m.x, m.y))))