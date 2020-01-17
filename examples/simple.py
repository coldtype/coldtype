from coldtype.animation import *

def render(f):
    return StyledString("abcdefg".upper(), Style("ç/MutatorSans.ttf", 300, wdth=1, wght=0.5, tl=-100)).fit(800).pens().align(f.a.r).f(1).reversePens().interleave(lambda p: p.s(0).sw(5))

animation = Animation(render)