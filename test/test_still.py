from coldtype.animation import *

def render(f):
    return [
        Slug("Test".upper(), Style("ç/MutatorSans.ttf", 500, wght=1, wdth=1, fill="darkorchid", r=1, t=-250)).fit(f.a.r.w-500).pens().align(f.a.r).interleave(lambda p: p.s(1).sw(50)),
        DATPen().gridlines(f.a.r).s("deeppink", 0.1).sw(10),
    ]

animation = Animation(render, (1920, 1080), bg=1)