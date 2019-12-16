from coldtype.animation import *

def render(f):
    kick, _ = ease("eei", f.a.t[0].valueForFrame("kick", f.i, preverb=5, reverb=10).value)
    rim, _ = ease("cei", f.a.t[0].valueForFrame("rimshot", f.i, preverb=3, reverb=10).value)
    bongo, _ = ease("eei", f.a.t[0].valueForFrame([45, 47], f.i, preverb=0, reverb=20).value)
    cowbell, _ = ease("eei", f.a.t[0].valueForFrame(39, f.i, reverb=10).value)
    strings = [
        StyledString("Bongo".upper(), Style("≈/MutatorSans.ttf", 100, r=1, ro=1, wdth=0, wght=0.5, t=-10+30*bongo, rotate=90*bongo)),
        StyledString("Click".upper(), Style("≈/MutatorSans.ttf", 150, r=1, ro=1, wdth=0.2, wght=0.7, t=-20+20*rim, rotate=-90*rim)),
        StyledString("Kick".upper(), Style("ç/MutatorSans.ttf", 160, r=1, ro=1, wdth=0.5+kick*0.5, wght=1, t=-20-70*kick)),
    ]
    graf = Graf(strings, f.a.r, leading=30)
    return graf.pens().align(f.a.r).f(1, 1-cowbell, 1-cowbell/2).interleave(lambda p: p.f(None).s(0).sw(10))


timeline = MidiTimeline(sibling(__file__, "test_midi/test_midi.mid"), storyboard=[0, 15], note_names={36:"kick",37:"rimshot",39:"conga",45:"bongolo",47:"bongohi"})
print(timeline[0].allNotes())

animation = Animation(render, (1080, 1080), timeline, bg=0)