


from coldtype import *
from coldtype.warping import warp_fn

@animation((1440, 1080), bg=hsl(0.5))
def render(f):
    xx = CMC.get(78, 0.5)*1000
    return [
        DATPen().rect(f.a.r).f(Gradient.Vertical(f.a.r, hsl(0.7), hsl(0.9))),
        (StyledString("Midi",
            Style("~/Type/fonts/fonts/ObviouslyVariable.ttf", 10+CMC.get(79, 0.5)*1000,
                slnt=CMC.get(80, 0.5),
                wdth=CMC.get(81, 0.5),
                wght=CMC.get(82, 0.5),
                tu=CMC.get(83, 0.5)*300-150,
                r=1,
                ro=1))
            .pens()
            .align(f.a.r)
            .pmap(lambda i,p: (p
                .flatten(5)
                .nlt(warp_fn(xx, xx, mult=1+CMC.get(84, 0.5)*200))))
            .f(1)
            .understroke(sw=CMC.get(77, 0.5)*20+1))]