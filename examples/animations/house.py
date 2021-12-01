from coldtype import *

audio = __sibling__("media/house.wav")

midi = (Programs.Midi(
    __sibling__("media/house.mid"),
    text=0, bpm=120, duration=60)
    .show())

@animation(timeline=midi.t, bg=0.1, audio=audio)
def render(f):
    k = f.t.ki(36).adsr([12, 10])
    s = f.t.ki(38).adsr([4, 35])
    c = f.t.ki(48).adsr([0, 50])

    hat = f.a.t.ki(42).index()
    hues = (0.6, 0.05) if hat < 2 else (0.75, 0.9)

    style = dict(
        font=Font.ColdObvi(),
        fontSize=500,
        tu=-150,
        ro=1)
    
    return (PS([
        (StSt("COLD", style, wdth=1-s*0.5))
            .f(hsl(hues[0], 0.75, 0.5))
            .î(1, λ.rt((hat+1)*-45)),
        (StSt("TYPE", style, tu=-150-100*k, rotate=-8*k))
            .f(hsl(hues[1], 0.75, 0.5))
            .î([2, 1], λ.t(70*c, 0))])
        .xalign(f.a.r)
        .stack(30)
        .align(f.a.r.inset(0, 150))
        .map(λ.rp().understroke(sw=10))
        .rotate(5))