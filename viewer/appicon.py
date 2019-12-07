from coldtype.animation import *

def render(f):
    fill = (0.5, 0.3, 0.7)
    if f.i <= 128:
        st = Style("ç/MutatorSans.ttf", 700, slnt=1, wght=1, wdth=0.15, fill=1, reverse=1, t=-50, removeOverlap=1)
        pen = Slug("C", st).pen().align(f.a.r, th=1, tv=1)
        return [
            DATPen(fill=(0)).oval(f.a.r.inset(10)),
            pen,
        ]
    else:
        st = Style("ç/MutatorSans.ttf", 300, slnt=1, wght=1, wdth=0.5, fill=1, reverse=1, t=-50, ss01=1, removeOverlap=1, kern=dict(Y=(-200, 0), P=(-250, 0), E=(-500, 0)))
        graf = Graf([Slug("Cold".upper(), st), Slug("type".upper(), st)], f.a.r.inset(150), leading=0)
        pens = graf.fit().pens().reversePens().align(f.a.r)\
            .interleave(lambda p: [p.attr(stroke=0, strokeWidth=35), p.copy().attr(fill=(0, 0.3))])
        pens.pens[0].translate(50, -20)
        pens.pens[1].translate(-60, -10)
        outline = pens.copy().pen().removeOverlap()
        return [
            DATPen().f(0).oval(f.a.r.inset(10)),
            pens,
        ]

animation = Animation(render, (1024, 1024), Timeline(1, storyboard=[16, 1024]), bg=None)