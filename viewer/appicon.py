from coldtype.animation import *

def render(f):
    fill = (0.5, 0.3, 0.7)
    if f.i < 128:
        st = Style("≈/ObviouslyVariable.ttf", 800, slnt=1, wght=0.85, wdth=0.5, fill=1, reverse=1, t=-50, ss01=1, removeOverlap=1)
        pen = Slug("C", st).pen().align(f.a.r)
        return [
            DATPen(fill=(0)).oval(f.a.r.inset(0)),
            pen,
        ]
    else:
        st = Style("≈/ObviouslyVariable.ttf", 400, slnt=1, wght=1, wdth=0.5, fill=1, reverse=1, t=-50, ss01=1, removeOverlap=1, kern=dict(E=(-120, 0)))
        graf = Graf([Slug("Cold".upper(), st), Slug("type".upper(), st)], f.a.r.inset(150), leading=-30)
        pens = graf.fit().pens().reversePens().align(f.a.r)\
            .interleave(lambda p: [p.attr(stroke=0, strokeWidth=30), p.copy().attr(fill=(0, 0.3))])
        pens.pens[0].translate(50, 0)
        pens.pens[1].translate(-40, 20)
        outline = pens.copy().pen().removeOverlap()
        return [
            DATPen(fill=(0)).oval(f.a.r.inset(0)),
            pens,
        ]

animation = Animation(render, (1024, 1024), Timeline(1, storyboard=[16, 1024]), bg=None)