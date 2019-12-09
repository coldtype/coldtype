from coldtype.animation import *

def render(f):
    at = f.a.progress(f.i, loops=1, easefn=["exp_io", "exp_io"])
    r = at.e*180 if at.loop_phase == 0 else 180+(180*(1-at.e))
    return [Slug("rotator".upper(), Style("ç/MutatorSans.ttf", 150, wght=at.s, wdth=1-at.e, t=-50*at.s, removeOverlap=True)).pens().align(f.a.r).f(0.7, 0.1, 0.3).rotate(r)]

animation = Animation(render, (1920, 1080), Timeline(30, storyboard=[0, 1]), bg=0)