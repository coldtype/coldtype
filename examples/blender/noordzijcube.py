from coldtype import *
from coldtype.blender import *

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

d = 5

@b3d_animation(timeline=120, center=(0, 1))
def cube(f):
    def entry(g, x, y, z):
        return (StSt("A", fnt,
            f.e("seio", 1, rng=(50, 550)),
            ro=1,
            wght=x/(d-1),
            wdth=(y/(d-1)),
            slnt=(z/(d-1)))
            .pen()
            .f(None).s(0).sw(1)
            .f(1)
            .align(g)
            .ch(b3d_pre(lambda p: p.fssw(1, -1, 0)))
            .ch(b3d(lambda bp: (bp
                .extrude(0.1+x/(d-1)*0.1)
                .rotate(90)
                .locate(0, 10.8*(z/d), 0)))))

    gs = f.a.r.grid(d, d)
    out = DPS()
    gi = 0
    gs = gs * d
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
                out += entry(gs[gi], x, y, z)
                gi += 1
    return out