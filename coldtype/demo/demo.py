from coldtype import *

states = [
    dict(wdth=0, rotate=0, tu=300),
    dict(wdth=1, rotate=15, tu=-150),
    dict(wdth=0.5, rotate=270, tu=0),
    dict(wdth=1, rotate=25, tu=50)
]

loop = Loop(70, 12, len(states))
co = Font.Cacheable(__sibling__("ColdtypeObviously-VF.ttf"))

@animation((1080, 1080/2), timeline=loop, storyboard=[0], bg=1)
def render(f):
    state = f.a.t.current_phase(f.i).calc_state(states)
    return (StSt("COLD",
        co, 350, fill=0, **state, r=1, leading=80)
        .pens()
        .align(f.a.r)
        .f(0)
        .understroke(s=1, sw=20))