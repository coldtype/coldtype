from coldtype.test import *
from random import Random

rnd = Random()
rnd.seed(0)

tl = Timeline(24)

@animation((250, 250), bg=0, timeline=tl)
def flyinga(f):
    return [
        P(f.a.r).f(hsl(f.e("qeio", 0), s=0.6)),
        (StSt("A", Font.MutatorSans(), 50, wght=0.2)
            .align(f.a.r)
            .scale(f.e("eei", 0, r=(1, 50)))
            .rotate(f.e("sei", 0, r=(0, 360)))
            .f(1))]

flyinga_contact = flyinga.contactsheet(4, slice(0, None, 2))

@animation((250, 250), bg=0, timeline=tl)
def storyboard(f):
    return [
        P(f.a.r).f(hsl(f.e("qeio", 0))),
        (StSt("E", Font.ColdtypeObviously(), 50, wdth=1)
            .align(f.a.r)
            .scale(f.e("eei", 0, r=(1, 50)))
            .rotate(f.e("sei", 0, r=(0, 360)))
            .f(1))]

storyboard_contact = storyboard.contactsheet(4, [0, 4, 8, 16])

def release(passes):
    flyinga.make_gif(passes)
    storyboard.make_gif(passes)