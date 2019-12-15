from coldtype.animation import *

def render(f):
    cg = f.a.t.trackClipGroupForFrame(0, f.i, styles=[1])
    print(cg.currentWord())
    return []

timeline = PremiereTimeline(sibling(__file__, "test_timeline.json"))
print(timeline)
animation = Animation(render, (1920, 1080), timeline, bg=0)