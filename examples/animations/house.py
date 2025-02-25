from coldtype import *

audio = ººsiblingºº("media/house.wav")

midi = MidiTimeline(
    ººsiblingºº("media/house.mid")
    , bpm=120
    , duration=60)

@animation(timeline=midi, bg=0.1, audio=audio, release=λ.export("h264", loops=4))
def render(f):
    k = f.t.ki(36).adsr([12, 10])
    s = f.t.ki(38).adsr([4, 35])
    c = f.t.ki(48).adsr([0, 50])

    hat = f.t.ki(42).index()
    hues = (0.6, 0.05) if hat < 2 else (0.75, 0.9)

    style = dict(font=Font.ColdObvi(), fontSize=500, tu=-150, ro=1)
    
    return (P(
        StSt("COLD", style, wdth=1-s*0.5)
            .f(hsl(hues[0], 0.75, 0.5))
            .index(1, lambda p: p.rt((hat+1)*-45)),
        StSt("TYPE", style, tu=-150-100*k, rotate=-8*k)
            .f(hsl(hues[1], 0.75, 0.5))
            .index([2, 1], lambda p: p.t(70*c, 0)))
        .xalign(f.a.r)
        .stack(30)
        .align(f.a.r.inset(0, 150))
        .map(lambda p: p.rp().ssw(0, 10).sf(1))
        .rotate(5))