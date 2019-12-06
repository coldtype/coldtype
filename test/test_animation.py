from coldtype.animation import *

def render(f):
    a = loop(f.a.prg(f.i), times=1, easefn=["eeio", "seio"])
    return [Slug("Coldtype".upper(), Style("ç/MutatorSans.ttf", 150, wght=0.5, wdth=a, removeOverlap=True)).pens().align(f.a.r).f(0.5, 0.4, 1)]

animation = Animation(render, (1920, 1080), Timeline(30, storyboard=[0, 15]), bg=1)