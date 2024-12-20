from coldtype import *

# inspired by https://github.com/coldtype/coldtype/discussions/135

letters = "".join([f"{x} " for x in "abcdefg<"])
at = AsciiTimeline(20, 30, "<\n"+letters).inflate()

ease_curve1 = P().withRect(1000, lambda r, p: p
    .moveTo(r.psw)
    .boxCurveTo(r.pc, "NW", (.95, .65))
    .boxCurveTo(r.pne, "SE", (.75, .95)))

ease_curve2 = P().withRect(1000, lambda r, p: p
    .moveTo(r.psw)
    .boxCurveTo(r.pc, "NW", (.95, .95))
    .boxCurveTo(r.pne, "SE", (.65, .135)))

@animation((1080, 540), timeline=at, bg=1)
def letters_easing(f):
    l = at.current(0).now()
    
    e1 = l.e(ease_curve1, 0)
    e2 = l.e(ease_curve2, 0, rng=(-360, 360))

    w = f.a.r.w + 140

    return (P(
        ease_curve1.copy()
            .fssw(-1, hsl(0.6, a=0.5), 4)
            .scale(0.5, point=(0,0))
            .align(f.a.r),
        ease_curve2.copy()
            .fssw(-1, hsl(0, a=0.5), 4)
            .scale(0.5, point=(0,0))
            .align(f.a.r),
        StSt(l.name, Font.RecMono(), 20)
            .align(f.a.r.take(100, "N")),
        StSt(l.name.upper(), Font.RecMono(), 250)
            .align(f.a.r)
            .f(0)
            .insert(0, lambda p: P(p.ambit().inset(2))
                .f(hsl(0.3, a=0.5)))
            .t(-w/2+w*e1, 0)
            .rotate(e2)))