from coldtype.animation import *

def render(f):
    kick, _ = ease("eei", f.a.t[0].valueForFrame(36, f.i, preverb=5, reverb=10).value)
    rim, _ = ease("eei", f.a.t[0].valueForFrame(37, f.i, preverb=7, reverb=15).value)
    strings = [
        StyledString("Click".upper(), Style("≈/MutatorSans.ttf", 150, r=1, ro=1, wdth=0, wght=0.7, t=-20+20*rim, rotate=-90*rim)),
        StyledString("Kick".upper(), Style("ç/MutatorSans.ttf", 160, r=1, ro=1, wdth=0.5+kick*0.5, wght=1, t=-20-70*kick)),
    ]
    graf = Graf(strings, f.a.r, leading=30)
    return graf.pens().align(f.a.r).f(1).interleave(lambda p: p.f(None).s(0).sw(10))


timeline = MidiTimeline(sibling(__file__, "test_midi/test_midi.mid"), storyboard=[0, 15])
animation = Animation(render, (1080, 1080), timeline, bg=0)