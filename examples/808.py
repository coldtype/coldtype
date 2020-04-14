from coldtype import *
from coldtype.animation.midi import MidiReader

hyperscrypt = Font("ç/NumericHyperScrypt.ufo")
drums = MidiReader("examples/media/808.mid", duration=120, bpm=120)[0]

print(drums.all_notes())

@animation(duration=drums.duration, bg=0, storyboard=[30])
def render(f):
    pens = StyledString("808", Style(hyperscrypt, 400)).pens().align(f.a.r)

    # nudge the upper piece between the 8 and 0
    m2 = lambda c: c.translate(0, 50)
    pens[0].mod_contour(0, m2)
    pens[1].mod_contour(0, m2)

    # nudge the lower piece between the 0 and 8
    m1 = lambda c: c.translate(0, -50)
    pens[1].mod_contour(3, m1)
    pens[2].mod_contour(3, m1)

    snare = drums.fv(f.i, [42], [3, 50]).ease()
    #m3 = lambda c: c.translate(250*snare, 0).scale(1+1*snare, center=f.a.r.point("C"))
    #pens[0].mod_contour(2, m3)
    #pens[0].mod_contour(3, m3)
    #m3 = lambda c: c.translate(-250*snare, 0).scale(1+1*snare, center=f.a.r.point("C"))
    #pens[2].mod_contour(1, m3)
    #pens[2].mod_contour(0, m3)

    # rotate the center
    kick = drums.fv(f.i, [36], [5, 50]).ease()
    r1 = lambda c: c.rotate(f.a.prg(f.i).e*360, point=f.a.r.point("C"))
    pens[1].mod_contour(4, lambda c: c.translate(kick*-50, 0)).mod_contour(4, r1)
    pens[1].mod_contour(5, lambda c: c.translate(kick*50, 0)).mod_contour(5, r1)

    h = f.a.progress(f.i).e
    return [
        DATPen().rect(f.a.r).f(hsl(0.8, l=.25)),
        pens.pen().removeOverlap().f(hsl(0.8, 0.75, 0.75)).scale(1+snare*0.5, center=f.a.r.point("C"))
    ]