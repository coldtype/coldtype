from coldtype import *
from coldtype.fx.skia import freeze

# Freeze!
# Kind of like freezing a track in a DAW,
# this lets you wrap expensive drawings with a freeze function
# that rasterizes to an image and saves that image in-memory
# (cache keyed by the source of the lambda passed in)
# thereby substituting a calculated vector with its "frozen"
# rasterized representation

r = Rect(1080, 540)
rs1 = random_series(r.mnx-100, r.mxx, 10+int(random()*40))
rs2 = random_series(r.mny-100, r.mxy, 1)
rs3 = random_series(seed=3)
rs4 = random_series(seed=2)
rs5 = random_series(0.50, 0.70, seed=4)

@renderable(r)
def scratch(r):
    def color(h):
        return hsl(h, 0.95, a=0.15)

    def freezeable():
        return (P().enumerate(range(0, 5000), lambda x:
                StSt("F", Font.MuSan(), 120, wght=rs3[x.i], wdth=rs4[x.i])
            .t(rs1[x.i], rs2[x.i])
            .f(color(rs5[x.i]))))

    return (P(
        freeze(1, 1, freezeable, additionals=[color, rs5]),
        StSt("F IS FROZEN", Font.MuSan(), 10+random()*100)
            .align(r).f(1)))
        
