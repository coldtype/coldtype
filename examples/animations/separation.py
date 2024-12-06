from coldtype import *

# variation on a design by @mjmeilleur

@animation(tl=240, bg=1)
def separation(f):
    e, info = f.e("eeio", 4, loop_info=True)
    seed = info//2
    extent = 160 + 100*seed
    
    rx = random_series(-extent, extent, seed=1+seed)
    ry = random_series(-extent, extent, seed=2+seed)
    rs = random_series(0, seed, seed=4+seed)
    rr = random_series(-360*2, 360*2, seed=3+seed)

    s = Scaffold(f.a.r.inset(300)).numeric_grid(4)
    
    return (P().enumerate(s, lambda x: P()
        .rect(x.el.r.inset(12))
        .outline(4))
        .layer(
            lambda p: p.f(hsl(0.9, 0.8)),
            lambda p: p.f(hsl(0.17, 0.8, 0.6)),
            lambda p: p.f(hsl(0.65, 0.8, 0.6)))
        .collapse()
        .map(lambda i, p: p
            .t(rx[i]*e, ry[i]*e)
            .scale(1+rs[i]*e)
            .rotate(rr[i]*e))
        .blendmode(BlendMode.Cycle(13)))