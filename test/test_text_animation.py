from coldtype.animation import *

def render(f):
    cg = f.a.t.trackClipGroupForFrame(0, f.i, styles=[1])
    print(cg.currentWord())
    return Slug(cg.currentWord()[0].ftext().upper(), Style("≈/ObviouslyVariable.ttf", 300, wdth=0.5, wght=1, slnt=1, fill="random")).pen().align(f.a.r)

timeline = PremiereTimeline(sibling(__file__, "test_timeline.json"))
print(timeline.trackClipGroupForFrame(0, timeline.cti))
animation = Animation(render, (1920, 1080), timeline, bg=0)