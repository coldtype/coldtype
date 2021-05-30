from coldtype.test import *
from random import Random

rnd = Random()
rnd.seed(0)

tl = Timeline(24)

@animation((250, 250), storyboard=[0], bg=0, timeline=tl)
def flyinga(f):
    qeio = f.a.progress(f.i, easefn="qeio").e
    eei = f.a.progress(f.i, easefn="eei").e
    return [
        (DATPen()
            .rect(f.a.r)
            .f(hsl(qeio, s=0.6))),
        (StyledString("A",
            Style(mutator, 50, wght=0.2))
            .pen()
            .align(f.a.r)
            .scale(1+50*eei)
            .rotate(360*qeio)
            .f(1))]

flyinga_contact = flyinga.contactsheet(4, slice(0, None, 1))

@animation((250, 250), storyboard=[0], bg=0, timeline=tl)
def storyboard(f):
    qeio = f.a.progress(f.i, easefn="qeio").e
    eei = f.a.progress(f.i, easefn="eei").e
    return [
        (DATPen()
            .rect(f.a.r)
            .f(hsl(qeio))),
        (StyledString("E",
            Style(co, 50, wdth=1))
            .pen()
            .align(f.a.r)
            .scale(1+50*eei)
            .rotate(360*qeio)
            .f(1))]

storyboard_contact = storyboard.contactsheet(4, [0, 4, 8, 16])

def release(passes):
    flyinga.make_gif(passes)
    storyboard.make_gif(passes)