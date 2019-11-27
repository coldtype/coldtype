from coldtype.animation import *

def render(f):
    return [Slug("Cldtyp".upper(), Style("≈/ObviouslyVariable.ttf", 300, slnt=1, wght=1, wdth=f.a.progress(f.i), fill=(0.5, 0.4, 1), reverse=1, t=-5, removeOverlap=True)).fit(f.a.r.w-500).pens().align(f.a.r).interleave(lambda p: p.attr(stroke=1, strokeWidth=10))]

animation = Animation(render, (1920, 1080), Timeline(30, storyboard=[0, 29]), bg=1)