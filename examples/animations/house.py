from coldtype import *
from coldtype.time.midi import *


#wav = __sibling__("media/house.wav")
#obvs = Font("assets/ColdtypeObviously-VF.ttf")
#midi = Path("examples/animations/media/house.mid").resolve()
#drums = MidiReader(midi, duration=60, bpm=120)[0]

audio = __sibling__("media/house.wav")
midi = Programs.Midi(__sibling__("media/house.mid"), text=0, bpm=120, duration=60)
drums = midi.t[0]

midi.hide()

@animation(timeline=midi.t, storyboard=[0], bg=0.1, audio=audio)
def render(f):
    kick = drums.fv(f.i, [36], [12, 10]).ease()
    snare = drums.fv(f.i, [38], [4, 35]).ease()
    hat_count = drums.fv(f.i, [42], [0, 1]).count
    cowbell = drums.fv(f.i, [48], [0, 50]).ease()
    chord_change = hat_count < 3

    style = Style(Font.ColdtypeObviously(), 500,
        tu=-150, r=1, ro=1)

    hues = (0.6, 0.05) if chord_change else (0.75, 0.9)
    
    return (PS([
        (StSt("COLD",
            style.mod(wdth=1-snare*0.5))
            .f(hsl(hues[0], 0.75, 0.5))
            .index(2, lambda c: c.rotate(hat_count*-45))),
        (StSt("TYPE",
            style.mod(
                tu=-150-100*kick,
                rotate=-8*kick))
            .f(hsl(hues[1], 0.75, 0.5))
            .index([1, 1], lambda c: c
                .translate(70*cowbell, 0)))])
        .reverse_pens()
        .xalign(f.a.r)
        .distribute(v=1)
        .track(-30, v=1) # should not be negative
        .map(lambda p: p.understroke(sw=10))
        .align(f.a.r.inset(0, 150))
        .rotate(5))

    type_pens = (StSt("TYPE",
        style.mod(
            tu=-150-100*kick,
            rotate=-8*kick))
        .cond(chord_change,
            lambda p: p.f(hsl(0.05, 0.75, 0.5)),
            lambda p: p.f(hsl(0.9, 0.75, 0.5)))
        .index([1, 1], lambda c: c
                .translate(70*cowbell, 0)))

    r = f.a.r.inset(0, 150)
    return DATPens([
        cold_pens.align(r, y="maxy").understroke(sw=10),
        type_pens.align(r, y="miny").understroke(sw=10).translate(-15, 0)
    ]).rotate(5)
