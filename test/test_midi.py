from coldtype.test import *
from coldtype.animation.midi import *

drums = MidiReader(Path("assets/loop2.mid").resolve(), duration=60, bpm=120)[0]

@animation(duration=drums.duration, storyboard=[40], bg=0.1)
def test_midi_read(f):
    kick = drums.fv(f.i, [36], [0, 5], all=1)
    snare = drums.fv(f.i, [38], [4, 35]).ease()
    hat = drums.fv(f.i, [42], [12, 12]).ease()
    hat_count = drums.fv(f.i, [42], [0, 1]).count
    cowbell = drums.fv(f.i, [48], [0, 50]).ease()

    #snare = 1
    #hat = 1

    #print(cowbell)

    style = Style(co, 500, tu=-150, r=1, ro=1)
    cold_pens = StyledString("COLD", style.mod(wdth=1-snare)).pens()
    type_pens = StyledString("TYPE", style.mod(tu=-150-50*hat, rotate=-15*hat)).pens()

    one_kick = hat_count < 3
    cold_pens.f(0.6j if one_kick else 0.75j, 0.75, 0.5)
    type_pens.f(0.05j if one_kick else 0.9j, 0.75, 0.5)

    def mod_p(idx, dp):
        if dp.glyphName == "P":
            o = dp.explode()
            o[1].translate(50*cowbell, 0)
            return o.implode()
    
    type_pens.map(mod_p)

    r = f.a.r.inset(0, 150)
    return [
        cold_pens.align(r, y="maxy").understroke(sw=10),
        type_pens.align(r, y="miny").understroke(sw=10)
    ]
