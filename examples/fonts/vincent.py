from coldtype import *
from coldtype.renderable.font import generativefont, glyphfn

r0 = Rect(500, 500)
rs = Rect(750, 1000).o(0,-250).grid(3, 4)
rs_extra = Rect(250, 1000).o(750,-250).grid(1,4)
rs = rs + rs_extra

o1 = 30
o2 = 10

rC0 = Rect(750-o1*2, 750-o1*2)
rC = rC0.grid(2, 2)

q1 = (P().oval(r0.inset(o1)).outline(o1)
    .intersection(P(rs[6]))
    .f(hsl(0.8)))

q2 = (P().oval(r0.inset(o1*2+20)).outline(o1)
    .intersection(P(rs[6]))
    .intersection(q1.copy())
    .f(hsl(0.6)))

q3 = (P().oval(rC0.inset(o1)).outline(o1)
    .intersection(P(rC[2]))
    .f(hsl(0.8)))

q4 = (P().oval(rC0.inset(o1*2+20)).outline(o1)
    .intersection(P(rC[2]))
    .intersection(q3.copy())
    .f(hsl(0.6)))

def cr(degree, ri, rotate, clip=None):
    q = [q1,q2,q3,q4][degree]
    _rs = rs if degree <= 1 else rC
    zero_frame = _rs[6] if degree <= 1 else _rs[2]
    
    _c = (q.copy()
        .addFrame(zero_frame)
        .align(_rs[ri], tx=0, ty=0)
        .rotate(rotate*90, point=_rs[ri].pc, tx=0, ty=0))
    
    if clip:
        for _clip in clip:
            _c = _c.difference(P(_rs[ri].take(o2/2, _clip)))
    
    return _c

def li(degree, ri, edges, clip=None):
    _rs = rs if degree <= 1 else rC
    minor = degree == 1 or degree == 3
    _c = P(_rs[ri].take(o1*2, edges[0]).drop(0 if not minor else o1*2-o2, edges[1] if len(edges) > 1 else edges[0])).f(hsl(0.3) if minor else hsl(0.6))

    if clip:
        for _clip in clip:
            _c = _c.difference(P(_rs[ri].take(o2/2, _clip)))
        
    return _c

def di(*pts):
    return P().line(pts).outline(o2/2, cap="butt")

@glyphfn(300)
def space(r):
    return P()

@glyphfn("auto")
def a(_):
    return P(
        cr(0,3,3,"ES"), cr(0,4,2,"WS"), cr(0,6,0,"N"),
        cr(1,7,1,"N"),
        li(1,4,"E","S"), li(0,7,"E","N"))

@glyphfn("auto")
def b(_):
    return P(
        li(0,0,"E"), li(1, 3, "EW"), li(0,6,"E","N"),
        cr(0,4,2,"S"), cr(0,7,1, "N"))

@glyphfn("auto")
def c(_):
    return P(
        cr(0,3,3,"ES"), cr(0,6,0,"N"))

@glyphfn("auto")
def d(_):
    return P(
        cr(0,3,3,"S"), cr(0,6,0,"N"),
        li(0,1,"W"), li(1,4,"WE"), li(0,7,"W"))

@glyphfn("auto")
def e(_):
    return P(
        cr(0,3,3,"ES"),
        cr(0,6,0,"N"),
        cr(0,4,2,"W"),
        li(0,4,"S").drop(40, "E").t(0,-o2/2),
        di(rs[3].psw, rs[4].pse).drop(o1*2,"W"))

@glyphfn("auto", 0)
def f(_):
    return P(
        cr(0,1,3,"ES"),
        di(rs[0].psw, rs[1].pse).drop(110,"W").drop(70, "E"),
        li(0,3,"E","S"),
        li(0,6,"E","N"))

@glyphfn("auto")
def g(_):
    return P(
        cr(0,3,3,"ES"), cr(0,6,0,"N"),
        li(0,3,"E","E").drop(40, "N"),
        li(1,3,"EW"), li(1,6,"EW"),
        cr(0,9,5))

@glyphfn("auto")
def h(_):
    return P(
        li(0,0,"E"), li(1,3,"EW"), li(0,6,"E"),
        cr(0,4,2,"S"), li(0,7,"E","N"))

@glyphfn("auto")
def i(_):
    return P(
        li(0,0,"E","S").take(o1*2,"N"),
        li(0,3,"E","NS"), li(0,6,"E","N"))

@glyphfn("auto", 0)
def j(_):
    return P(
        li(0,0,"E","S").take(o1*2,"N"),
        li(0,3,"E","NS"), li(0,6,"E","N"),
        cr(0,9,1,"N").t(0,-o2/2))

@glyphfn("auto")
def k(_):
    return P(
        li(0,1,"W"), li(1, 4, "WE"), li(1,7,"WE"),
        cr(0,4,5), cr(0,7,2))

@glyphfn("auto")
def l(_):
    return P(
        li(0,0,"E","S"),
        li(0,3,"E","NS"), li(0,6,"E","N"))

@glyphfn("auto")
def m(_):
    return P(
        li(0,7,"W","N"),
        li(0,4,"W","S").drop(40,"N"), cr(0,4,2,"S"),
        di(rs[5].pnw,rs[8].psw).reverse(),
        cr(0,5,2,"S"), li(0,8,"E","N"))

@glyphfn("auto")
def n(_):
    return P(
        li(0,7,"W","N"),
        li(0,4,"W","S").drop(40,"N"), cr(0,4,2,"S"),
        li(0,7,"E","N"))

@glyphfn("auto")
def o(_):
    return P(
        cr(0,3,3,"ES"), cr(0,6,0,"NE"),
        cr(0,4,2,"WS"), cr(0,7,5,"NW"))

@glyphfn("auto")
def p(_):
    return P(
        cr(0,3,3,"ES"), cr(0,4,2,"WS"), cr(0,7,5,"N"),
        cr(1,6,0,"N"),
        li(0,6,"W","NS"), li(0,9,"W","N"))

@glyphfn("auto")
def q(_):
    return P(
        cr(0,3,3,"ES"), cr(0,4,2,"WS"), cr(0,6,0,"N"),
        cr(1,7,1,"N"),
        li(0,7,"E","NS"), li(0,10,"E","N"))

@glyphfn("auto")
def r(_):
    return P(
        cr(0,3,3,"ES"), li(0,6,"W","N"), li(1,3,"WE","S"))

@glyphfn("auto")
def s(_):
    return P(
        cr(0,6,1), cr(0,4,3))

@glyphfn("auto", 0)
def t(_):
    return P(
        cr(0,1,0),
        di(rs[0].psw, rs[1].pse).drop(150,"W"),
        li(0,4,"W","S"),
        cr(0,7,0,"N"))

@glyphfn("auto")
def u(_):
    return P(
        li(0,3,"W","S"), cr(0,6,0,"NE"),
        li(0,4,"E","S"), cr(0,7,5,"NW"))

@glyphfn("auto")
def v(_):
    return P(
        li(0,4,"W","S"),
        li(0,7,"W","N").drop(40,"S"), cr(0,7,1,"N"),
        li(0,4,"E","S"))

@glyphfn("auto")
def w(_):
    return m.func(_).rotate(180)

@glyphfn("auto")
def x(_):
    return P(
        cr(0,3,2,"S"), cr(0,6,1,"N"),
        cr(0,4,3,"S"), cr(0,7,0,"N"))

@glyphfn("auto")
def y(_):
    return P(
        li(0,3,"W","S"), cr(0,6,0,"N"),
        li(1,7,"WE"), li(0,4,"W"),
        li(0,10,"W"))

@glyphfn("auto")
def z(_):
    return P(
        li(0,3,"N","S"),
        li(1,3,"EW"),
        cr(0,6,3),
        li(0,6,"S").drop(40,"W"))

@glyphfn("auto")
def germandbls(_):
    return P(
        li(0,0,"E"), cr(0,1,2),
        li(1, 3, "EW"), li(0,6,"E"),
        di(rs[4].pnw, rs[4].pne).reverse().drop(o2,"W"),
        cr(0,4,2,"S").drop(o2,"W"),
        cr(0,7,1,"N").drop(o2,"W"))

@glyphfn("auto")
def ae(_):
    return P(
        P(
            cr(0,3,3,"ES"), cr(0,4,2,"WS"), cr(0,6,0,"N"),
            cr(1,7,1,"N"),
            li(1,7,"E","N")),
        e.func(None).t(rs[5].x-o1*2, 0))

@glyphfn("auto")
def oslash(_):
    return (P(
        o.func(_),
        di(rs[6].psw, rs[4].pne).reverse()))

@glyphfn("auto")
def one(_):
    return (P(
        c:=cr(0,0,1).t(0,-o1*2),
        di(c.bounds().pne,rs[6].pse).reverse(),
        li(0,4,"W","S"), li(0,7,"W","N")))

@glyphfn("auto")
def two(_):
    return (P(
        P(cr(0,0,2,"S"), cr(0,3,1,"N")).t(0,-o1*2),
        li(1,6,"WE"),
        li(0,6,"S")))

@glyphfn("auto")
def three(_):
    return (P(
        cr(0,6,1,"N"), cr(0,3,2,"S"),
        c:=cr(0,0,1).drop(o1*2, "N"),
        di(c.ambit(tx=1,ty=1).pne,c.ambit(tx=1,ty=1).pnw).reverse()))

@glyphfn("auto")
def four(_):
    return (P(
        cr(0,0,1).drop(o1*2,"N"),li(0,3,"N"),
        di(rs[3].pne,rs[6].pse).reverse(),
        li(0,6,"E","N")))

@glyphfn("auto")
def five(_):
    return (P(
        li(0,0,"N").t(0,-o1*2),
        li(1,0,"WE").drop(o1*2,"N"),
        cr(0,3,2,"S"),cr(0,6,1,"N")))

@glyphfn("auto")
def six(_):
    _r0 = r0.inset(o1)
    start = _r0.pw.o(0,o2/2)
    end = start.o(45,150)
    return P(
        #cr(0,3,3,"ES"),
        P().m(start)
            .q(start.o(0,83), end)
            .l(_r0.pn.o(30,203))
            .ep()
            .outline(o1, cap="butt")
            .reverse(),
        cr(0,6,0,"NE"),
        cr(0,4,2,"S"), cr(0,7,5,"NW"),
        di(rs[4].pnw,rs[4].psw).reverse())

@glyphfn("auto")
def seven(_):
    return (P(
        cr(0,0,3).t(0, -o1*4),li(0,0,"N").t(0,-o1*2),
        li(0,6,"W","N")))

@glyphfn("auto")
def eight(_):
    return P(
        cr(0,0,0,"E").drop(o1*2,"N"),
        cr(0,1,1,"W").drop(o1*2,"N"),
        P(li(1,0,"NS"),li(1,1,"NS"))
            .t(0,-o1*2).inset(40,0),
        cr(0,3,3,"ES"), cr(0,6,0,"NE"),
        cr(0,4,2,"WS"), cr(0,7,5,"NW"))

@glyphfn("auto")
def nine(_):
    return six.func(_).rotate(180)

@glyphfn("auto")
def zero(_):
    return P(
        P(li(1,3,"WE"),li(1,4,"EW")).drop(60, "N"),
        P(cr(0,0,3,"E"), cr(0,1,2,"W")).t(0, -o1*2),
        cr(0,6,0,"E"), cr(0,7,5,"W"))

@glyphfn("auto")
def ampersand(_):
    return P(
        cr(0,0,0).drop(o1*2,"N"),
        P(li(1,0,"NS"),li(1,1,"NS")).t(0,-o1*2).inset(40,0),
        cr(0,3,3,"S"), cr(0,6,0,"NE"),
        cr(0,7,5,"W"),
        li(0,7,"N").drop(40, "E"))

@glyphfn("auto")
def question(_):
    return P(
        P(cr(0,0,2,"S"),cr(0,3,1,"N"),li(1,0,"WE"))
            .t(0,-o1*2),
        li(0,6,"W").take(o1*2,"S"))

@glyphfn("auto")
def exclam(_):
    return P(
        P(li(0,0,"W","S"),li(0,3,"W","N")).t(0,-o1*2),
        li(0,6,"W").take(o1*2,"S"))

@glyphfn("auto")
def A(_):
    return P(
        li(2,2,"W","N"),
        li(2,2,"E","N"),
        li(2,0,"E","S").drop(40, "N"),
        cr(2,0,3,"S"),
        di(rC[0].psw,rC[0].pse).reverse().inset(o1*2,0))

@glyphfn("auto")
def B(_):
    return P(
        li(2,2,"S","N").drop(40,"E"),
        cr(2,2,2),
        cr(2,0,2),
        di(rC[0].psw,rC[0].pse).reverse(),
        li(3,0,"WE"),
        li(3,2,"WE"))

@glyphfn("auto")
def C(_):
    return P(
        cr(2,2,0,"N"),
        cr(2,0,3,"S"))

@glyphfn("auto")
def D(_):
    return P(
        cr(2,2,1,"N"),
        cr(2,0,2,"S"),
        li(2,0,"W").drop(40,"N"),
        li(3,2,"WE").drop(10,"S"))

@glyphfn("auto")
def E(_):
    return P(
        li(2,2,"S","N").drop(40,"W"),
        cr(2,2,3),
        cr(2,0,3),
        di(rC[0].psw,rC[0].pse).reverse())

@glyphfn("auto")
def F(_):
    return P(
        cr(2,0,3,"S"),
        di(rC[0].psw,rC[0].pse).reverse().inset(o1*2, 0),
        li(2,2,"W","N"))

@glyphfn("auto")
def G(_):
    return P(
        cr(2,2,0,"N"),
        cr(2,0,3,"S"),
        di(rC[0].psw,rC[0].pse).reverse().drop(o1*2, "W"),
        li(2,2,"E").drop(40,"S"))

@glyphfn("auto")
def H(_):
    return P(
        cr(2,2,3,"E"), cr(2,0,0,"E"),
        cr(2,3,2,"W"), cr(2,1,1,"W"),
        li(3,0,"WE"), li(3,2,"WE"),
        li(3,1,"EW"), li(3,3,"EW"))

@glyphfn("auto")
def I(_):
    return P(
        li(2,2,"W","N"),
        li(2,0,"W","S"))

@glyphfn("auto")
def J(_):
    return P(
        cr(2,2,1,"N"),
        li(2,0,"E","S"))

@glyphfn("auto")
def K(_):
    return P(
        cr(2,2,2),
        cr(2,0,1),
        li(3,0,"WE"),
        li(3,2,"WE"))

@glyphfn("auto")
def L(_):
    return P(
        cr(2,2,0,"N"),
        li(2,0,"W","S"))

@glyphfn("auto")
def M(_):
    return P(
        cr(2,0,2),
        cr(2,1,2,"S"),
        li(2,0,"W","S").drop(40,"N"),
        li(2,2,"W","N"),
        li(2,3,"E","N"), 
        li(3,1,"WE"), li(3,3,"WE"))

@glyphfn("auto")
def N(_):
    return P(
        cr(2,0,2,"S"),
        li(2,0,"W","S").drop(40,"N"),
        li(2,2,"W","N"),
        li(2,2,"E","N"))

@glyphfn("auto")
def O(_):
    return P(
        cr(2,2,0,"NE"), cr(2,0,3,"SE"),
        cr(2,1,2,"WS"), cr(2,3,1,"NW"))

@glyphfn("auto", glyph_name="P")
def P_(_):
    return P(
        li(2,0,"W","S").drop(40,"N"),
        li(2,2,"W","N"),
        cr(2,0,2),
        di(rC[0].psw,rC[0].pse).reverse().drop(o1*2,"W"))

@glyphfn("auto")
def Q(_):
    _r0 = rC0.inset(o1)
    start = _r0.pw.o(0,-o2/2)
    end = start.o(75,-200)
    return P(
        cr(3,2,0,"N"), cr(2,0,3,"SE"),
        cr(2,1,2,"WS"), cr(3,3,1,"N"),
        cr(2,3,1,"N")
            .intersection(P()
                .m(rC0.pc).l(rC0.pse).l(rC0.pe).cp()),
        P().m(start)
            .q(start.o(0,-103), end)
            .l(_r0.ps.o(0,-133))
            .ep()
            .outline(o1, cap="butt")
            .reverse())

@glyphfn("auto")
def R(_):
    return P(
        cr(2,2,2),
        cr(2,0,2),
        li(3,0,"WE"),
        li(3,2,"WE"),
        li(2,0,"S").drop(40,"E"),
        di(rC[0].psw,rC[0].pse).reverse())

@glyphfn("auto")
def S(_):
    return P(
        cr(2,2,1),
        cr(2,1,3))

@glyphfn("auto")
def T(_):
    return P(
        cr(3,1,2),
        cr(2,0,3),
        li(2,0,"E","S").drop(40,"N"),
        li(2,2,"E","N"))

@glyphfn("auto")
def U(_):
    return P(
        cr(2,2,0,"NE"),
        li(2,1,"E","S"),
        li(2,0,"W","S"),
        cr(2,3,1,"NW"))

@glyphfn("auto")
def V(_):
    return P(
        li(2,2,"W","N").drop(40,"S"),
        li(2,0,"E","S"),
        li(2,0,"W","S"),
        cr(2,2,1,"N"))

@glyphfn("auto")
def W(_):
    return M.func(_).rotate(180)

@glyphfn("auto")
def X(_):
    return P(
        cr(2,2,1,"N"), cr(2,0,2,"S"),
        cr(2,1,3,"S"), cr(2,3,0,"N"))

@glyphfn("auto")
def Y(_):
    return P(
        cr(2,0,0),
        li(2,2,"E","N"),
        li(3,0,"EW","S"))

@glyphfn("auto")
def Z(_):
    return P(
        li(2,0,"N").drop(40,"E"),
        cr(2,0,1,"S"),
        li(2,2,"W","N"),
        li(2,2,"S"))

@glyphfn("auto")
def AE(_):
    return P(
        li(2,2,"W","N"),
        li(3,3,"WE","N"),
        li(3,1,"WE","S"),
        cr(2,0,3,"S"),
        di(rC[0].psw,rC[1].pse).reverse().drop(o1*2,"W"),
        cr(2,1,3),
        cr(2,3,3),
        li(2,3,"S").drop(40,"W"))

@glyphfn("auto")
def Oslash(_):
    return O.func(_) + di(rC[2].psw, rC[1].pne).reverse()

@glyphfn("auto", 0)
def period(_):
    return P(li(0,6,"E").take(o1*2,"S"))

@glyphfn("auto", 0)
def comma(_):
    return P(cr(0,6,1))

@glyphfn("auto", 0)
def semicolon(_):
    return P(
        #li(0,0,"E","S").take(o1*2,"N"),
        #li(0,3,"E","NS"), li(0,6,"E","N"),
        cr(0,6,1),
        li(0,3,"E").take(o1*2,"N"))

def show_grid(p):
    grid = (P().enumerate(rs, lambda x: P(
        StSt(str(x.i), Font.JBMono(), 100).align(x.el).f(hsl(0.7, a=0.3)),
        P(x.el).fssw(-1, hsl(0.9), 1))))
    
    #grid = P()
    
    grid.append(P()
        .line([rs[0].pnw.o(0,-o1*2),rs[12].pne.o(0,-o1*2)])
        .fssw(-1, hsl(0.7), 2))
    
    grid.append(P().enumerate(rC, lambda x: P(
        StSt(str(x.i), Font.JBMono(), 150).align(x.el).f(hsl(0.3, a=0.3)),
        P(x.el).fssw(-1, hsl(0.6), 1))))
    
    return grid.tag("guide") + p

@generativefont(globals(),
    ººsiblingºº("vincent.ufo"),
    "Vincent",
    "Regular",
    default_lsb=30,
    default_rsb=30,
    filter=show_grid
    )
def gufo(f):
    return gufo.glyphViewer(f)

@animation((1080, 300), tl=gufo.timeline)
def spacecenter(f):
    return gufo.spacecenter(f.a.r, "auto", idx=f.i)