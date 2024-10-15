from coldtype import *

# a coldtypification of https://github.com/djrrb/Python-for-Visual-Designers-Fall-2023/blob/main/session-4/code/2-BezierPathLoop.py

seed = 1
wobble = 250
handle_length = 100

rw1 = random_series(-wobble, wobble, seed=seed)
rw2 = random_series(-wobble, wobble, seed=seed+1)
rc = random_series(seed=seed+2)

@renderable(bg=1)
def shapes(r):
    def build_shape(x):
        return (P()
            .moveTo((0, 0))
            .lineTo((r.w, 0))
            .lineTo((r.w, h:=r.h*(1-x.e)))
            .curveTo(
                (r.w, h+handle_length+rw1[x.i]),
                (0, h+handle_length+rw2[x.i]),
                (0, h))
            .closePath()
            .f(hsl(rc[x.i], 0.6, 0.6, 0.5)))
    
    return (P().enumerate(range(0, 10), build_shape)
        .scale(0.75, pt=(0, 0))
        .xalign(r, "CX"))