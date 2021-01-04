from coldtype.test import *

states = [
    dict(wdth=0, rotate=0, tu=0),
    dict(wdth=1, rotate=15, tu=-150),
    dict(wdth=0.5, rotate=360, tu=0),
    dict(wdth=0.75, rotate=15, tu=300),
    dict(wdth=0.25, rotate=-180, tu=-800)
]

loop = Loop(120, len(states), 8)

@animation(timeline=loop, storyboard=[0], bg=0)
def render(f):
    state = f.a.t.current_phase(f.i).calc_state(states)
    return (StyledString("COLD",
        Style(co, 350, fill=0, **state, r=1))
        .pens()
        .align(f.a.r)
        .f(1)
        .understroke())