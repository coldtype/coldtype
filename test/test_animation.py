from coldtype.animation import *

def render(f):
    a, c = loop(f.a.prg(f.i), times=1, easefn=["exp_io", "eeio"], return_count=1)
    return [Slug("rotator".upper(), Style("ç/MutatorSans.ttf", 150, wght=1-a, wdth=a, removeOverlap=True)).pens().align(f.a.r).f(0.7, 0.1, 0.3).rotate(a*180 if c == 0 else 180+(180*(1-a)))]

animation = Animation(render, (1920, 1080), Timeline(30, storyboard=[5, 13, 27]), bg=0)