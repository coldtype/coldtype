from coldtype.test import *

tl = Timeline(26, fps=23.976, storyboard=[0], jumps=[5])

def find_workarea(self):
    return [0, 1, 2]

Timeline.find_workarea = find_workarea

@animation(rect=(1920, 1080), timeline=tl, bg=0)
def render(f):
    pe = f.a.t.progress(f.i, loops=1, easefn="qeio").e
    return DATPens([
        (StyledString(chr(65+f.i),
            Style(mutator, 1000, wdth=1-pe, wght=pe))
            .pen()
            .f(hsl(pe, s=0.6, l=0.6))
            .align(f.a.r)),
        (StyledString("{:02d}".format(f.i),
            Style(recmono, 72, wdth=1))
            .pens()
            .align(f.a.r.take(150, "mny"), th=0)
            .f(hsl((1-pe)+0.5)))])