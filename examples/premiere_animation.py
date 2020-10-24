from coldtype.test import *
from coldtype.animation.nle.premiere import PremiereTimeline

pt = PremiereTimeline("examples/test_coldtype.json")

@animation(timeline=pt, rect=(1920, 1080), bg=0)
def render(f):
    print("> frame:", f.i)
    
    def render_clip(f, idx, clip, t):
        return t.upper(), Style(mutator, 150, wght=1)
    
    cg = pt.clip_group(0, f)
    return (cg.pens(f, render_clip)
        .remove_futures()
        .f(1)
        .align(f.a.r))