from coldtype import *
from coldtype.renderable.font import generativefont, glyphfn

r0 = Rect(500, 500)
rs = Rect(750, 1000).o(0,-250).grid(3, 4)
rs_extra = Rect(250, 1000).o(750,-250).grid(1,4)

rs = rs + rs_extra

o1 = 30
o2 = 10

q1 = (P().oval(r0.inset(o1)).outline(o1)
    .intersection(P(rs[6]))
    .f(hsl(0.8)))

q2 = (P().oval(r0.inset(o1*2+20)).outline(o1)
    .intersection(P(rs[6]))
    .intersection(q1.copy())
    .f(hsl(0.6)))

def cr(degree, ri, rotate, clip=None):
    _c = ((q1 if degree == 0 else q2).copy()
        .addFrame(rs[6])
        .align(rs[ri], tx=0, ty=0)
        .rotate(rotate*90, point=rs[ri].pc, tx=0, ty=0))
    
    if clip:
        for _clip in clip:
            _c = _c.difference(P(rs[ri].take(o2/2, _clip)))
    
    return _c

def li(degree, ri, edges, clip=None):
    _c = P(rs[ri].take(o1*2, edges[0]).drop(0 if degree == 0 else o1*2-o2, edges[1] if len(edges) > 1 else edges[0])).f(hsl(0.3) if degree else hsl(0.6))

    if clip:
        for _clip in clip:
            _c = _c.difference(P(rs[ri].take(o2/2, _clip)))
        
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
    return P(
        li(0,4,"W","S"), cr(0,8,0,"N"),
        di(rs[5].pnw,rs[8].psw).reverse(),
        cr(0,7,0,"N"), li(0,5,"E","S"),
        li(0,8,"E","N").drop(40,"S"))

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

def show_grid(p):
    grid = (P().enumerate(rs, lambda x: P(
        StSt(str(x.i), Font.JBMono(), 100).align(x.el).f(hsl(0.7, a=0.3)),
        P(x.el).fssw(-1, hsl(0.9), 1))))
    
    grid.append(P()
        .line([rs[0].pnw.o(0,-o1*2),rs[12].pne.o(0,-o1*2)])
        .fssw(-1, hsl(0.7), 2))
    
    return grid.tag("guide") + p

@generativefont(globals(),
    ººsiblingºº("vincent.ufo"),
    "Vincent",
    "Regular",
    default_lsb=20,
    default_rsb=20,
    filter=show_grid
    )
def gufo(f):
    return gufo.glyphViewer(f)

@animation((1080, 300), tl=gufo.timeline)
def spacecenter(f):
    return gufo.spacecenter(f.a.r, "auto", idx=f.i)