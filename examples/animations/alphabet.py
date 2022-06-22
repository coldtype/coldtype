from coldtype.test import *

tl = Timeline(26, fps=18)

@animation(rect=(1080, 1080), timeline=tl, bg=0)
def render(f):
    pe = f.e(e:="qeio", 1)
    return (P(
        (StSt(chr(65+f.i), mutator
            , f.e(e, r=(500, 750))
            , wdth=1-pe
            , wght=pe)
            .fssw(-1, hsl(pe, s=0.6, l=0.6), 3)
            .align(f.a.r, tv=1)
            .translate(0, 50)
            .removeOverlap()),
        (StSt("{:02d}".format(f.i), recmono, 24, wdth=1)
            .pen()
            .align(f.a.r.take(150, "mny"), th=0)
            .f(hsl((1-pe)+0.5)))))

def didRenderAll(passes):
    for p in passes:
        print(p.output_path)