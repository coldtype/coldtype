from coldtype.animation import *

def render(f):
    return [Slug("Test".upper(), Style("≈/ObviouslyVariable.ttf", 300, slnt=1, wght=1, wdth=1, fill="random", reverse=1, t=-100)).fit(f.a.r.w-500).pens().align(f.a.r).interleave(lambda p: p.attr(stroke=1, strokeWidth=20))]

animation = Animation(render, (1920, 1080), bg=1)