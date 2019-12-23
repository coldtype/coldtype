from coldtype.animation import *

#r = normalize_color("random")
r = normalize_color("deeppink")

def render(f):
    cg = f.a.t.trackClipGroupForFrame(0, f.i, styles=[1])
    return [Slug(cg.currentSyllable().ftext().upper(), Style("ç/MutatorSans.ttf", 300, wdth=0, wght=1, fill=r)).pen().align(f.a.r), Slug("{:04d}".format(f.i), Style("/Library/Fonts/Andale Mono.ttf", 72, fill=0.2)).pen().align(f.a.r, th=0).translate(0, -200)]

timeline = PremiereTimeline(sibling(__file__, "test_timeline.json"))
animation = Animation(render, (1920, 1080), timeline, bg=0)