from coldtype.animation import *

def render(f):
    at = f.a.progress(f.i, loops=1, easefn="eeio")
    return StyledString("Hello, world".upper(), Style("ç/MutatorSans.ttf", 100, wdth=at.e, wght=at.e)).pens().align(f.a.r)

timeline = Timeline(120, storyboard=[0, 60, 119])
animation = Animation(render, timeline=timeline)