from coldtype import *
from coldtype.blender import *

@b3d_animation(tl=60)
def scratch(f):
    return (P()
        .roundedRect(f.a.r.inset(350), 130)
        .rotate(f.e("ceio", 1, rng=(-75, 75)))
        .f(hsl(0.65))
        .tag("single_shape")
        .ch(b3d(lambda p: p
            .extrude(1.5))))
