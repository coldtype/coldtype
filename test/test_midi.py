from coldtype.test import *
from coldtype.animation.midi import *


reader = MidiReader(Path("assets/loop.mid").resolve(), bpm=120)


@animation(duration=60, storyboard=[0, 50])
def test_midi_read(f):
    kick = reader[0].valueForFrame([36], f.i, all=1)
    snare = reader[0].valueForFrame([38], f.i, preverb=5, reverb=20)
    hat = reader[0].valueForFrame([42], f.i, preverb=3, reverb=10)
    cowbell = reader[0].valueForFrame([49], f.i, preverb=3, reverb=10)
    hues = [0.6j, 0.05j] if kick.count < 2 else [0.75j, 0.9j]

    def mod_p(idx, dp):
        if dp.glyphName == "P":
            o = dp.explode()
            o[1].translate(50*cowbell.ease(), 0)
            return o.implode()

    return [
        StyledString("COLD", Style(co, 500, tu=-150, r=1, ro=1, wdth=1-snare.ease())).pens().f(hues[0], 0.75, 0.5).align(f.a.r.inset(0, 150), y="maxy").understroke(sw=10),
        StyledString("TYPE", Style(co, 500, tu=-150, r=1, ro=1, wdth=1, rotate=15*hat.ease(eo="eei"))).pens().f(hues[1], 0.75, 0.5).align(f.a.r.inset(0, 150), y="miny").map(mod_p).understroke(sw=10)
    ]
