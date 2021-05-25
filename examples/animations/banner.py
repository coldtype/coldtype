from coldtype import *

states = [
    dict(wdth=0, rotate=0, tu=300),
    dict(wdth=1, rotate=15, tu=-150),
    dict(wdth=0.25, rotate=-15, tu=350),
    dict(wdth=0.75, rotate=0, tu=-175),
    dict(wdth=0.5, rotate=25, tu=100)
]

obvs = Font("assets/ColdtypeObviously-VF.ttf")
loop = Loop(200, 10, len(states))

@animation(timeline=loop, storyboard=[0], bg=1, rect=(1500, 300))
def render(f):
    phase = f.a.t.current_phase(f.i)
    state = phase.calc_state(states)
    return (StyledString("COLDTYPE",
        Style(obvs, 250, fill=0, **state, r=1, ro=1))
        .pens()
        .align(f.a.r)
        .f(0)
        .understroke(s=1, sw=15))