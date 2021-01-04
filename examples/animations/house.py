from coldtype import *
from coldtype.animation.midi import *


wav = __sibling__("media/house.wav")
obvs = Font("assets/ColdtypeObviously-VF.ttf")
midi = Path("examples/animations/media/house.mid").resolve()
drums = MidiReader(midi, duration=60, bpm=120)[0]


@animation(duration=drums.duration, storyboard=[0], bg=0.1, audio=wav)
def render(f):
    kick = drums.fv(f.i, [36], [12, 10]).ease()
    snare = drums.fv(f.i, [38], [4, 35]).ease()
    hat_count = drums.fv(f.i, [42], [0, 1]).count
    cowbell = drums.fv(f.i, [48], [0, 50]).ease()

    style = Style(obvs, 500, tu=-150, r=1, ro=1)
    cold_pens = StyledString("COLD", style.mod(wdth=1-snare*0.5)).pens()
    type_pens = StyledString("TYPE", style.mod(tu=-150-100*kick, rotate=-8*kick)).pens()

    chord_change = hat_count < 3
    cold_pens.f(hsl(0.6 if chord_change else 0.75, 0.75, 0.5))
    type_pens.f(hsl(0.05 if chord_change else 0.9, 0.75, 0.5))
    
    for o in cold_pens.glyphs_named("O"):
        o.mod_contour(1, lambda c: c.rotate(hat_count*-45))
    for p in type_pens.glyphs_named("P"):
        p.mod_contour(1, lambda c: c.translate(70*cowbell, 0))

    r = f.a.r.inset(0, 150)
    return DATPenSet([
        cold_pens.align(r, y="maxy").understroke(sw=10),
        type_pens.align(r, y="miny").understroke(sw=10).translate(-15, 0)
    ]).rotate(5)
