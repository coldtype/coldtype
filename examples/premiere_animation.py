from coldtype import *
from coldtype.animation.nle.premiere import PremiereTimeline


pt = PremiereTimeline("examples/test_coldtype.json")

@animation(timeline=pt, rect=(1920, 1080), bg=0.5)
def render(f):
    return DATPen().oval(f.a.r).f("random")