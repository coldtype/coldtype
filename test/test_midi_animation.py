from coldtype.animation import *

def render(f):
    kick, _ = ease("eei", f.a.t[0].valueForFrame(36, f.i, preverb=2, reverb=20).value)
    rim, _ = ease("eei", f.a.t[0].valueForFrame(37, f.i, preverb=3, reverb=30).value)
    return StyledString("Kick".upper(), Style("ç/MutatorSans.ttf", 150, wdth=0.5+kick*0.5, wght=0.5+kick*0.5, t=-20-50*kick, ss01=1, bs=rim*20, reverse=1)).pens().align(f.a.r).f(1).interleave(lambda p: p.f(None).s(0).sw(10))

timeline = MidiTimeline(sibling(__file__, "test_midi/test_midi.mid"), storyboard=[119])
animation = Animation(render, (1080, 1080), timeline, bg=0)