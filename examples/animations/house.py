from coldtype import *

audio = __sibling__("media/house.wav")
midi = Programs.Midi(__sibling__("media/house.mid"), text=0, bpm=120, duration=60)

midi.hide()

@animation(timeline=midi.t, bg=0.1, audio=audio)
def render(f):
    drums = midi.t[0]
    d = drums.fifve(f.i)
    kick = d([36], 12, 10)
    snare = d([38], 4, 35)
    cowbell = d([48], 0, 50)

    hat_count = drums.fv(f.i, [42], [0, 1]).count
    chord_change = hat_count < 3
    hues = (0.6, 0.05) if chord_change else (0.75, 0.9)

    style = Style(Font.ColdtypeObviously(), 500,
        tu=-150, ro=1)
    
    return (PS([
        (StSt("COLD",
            style.mod(wdth=1-snare*0.5))
            .f(hsl(hues[0], 0.75, 0.5))
            .î(1, λ.r(hat_count*-45))),
        (StSt("TYPE",
            style.mod(
                tu=-150-100*kick,
                rotate=-8*kick))
            .f(hsl(hues[1], 0.75, 0.5))
            .î([2, 1], λ.t(70*cowbell, 0)))])
        .xalign(f.a.r)
        .stack(30)
        .align(f.a.r.inset(0, 150))
        .map(λ.rp().understroke(sw=10))
        .rotate(5))