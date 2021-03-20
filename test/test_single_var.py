from coldtype.test import *
from drafting.text.richtext import RichText

tl = Timeline(300, fps=30)

@animation((1080, 1080), timeline=tl)
def test_multi_var(f):
    e = f.a.progress(f.i, loops=4, easefn="eeio").e
    e2 = f.a.progress(f.i, loops=5, easefn="eei").e
    fs = 200
    wght = (1-e)*0.85

    pens = (RichText(f.a.r, "T[t]/Y[y]/P[p]/E[e]", {
            "t": Style(mutator, fs, wdth=e, wght=wght),
            "y": Style(mutator, fs, wdth=1-e2, wght=wght),
            "p": Style(mutator, fs, wdth=e2, wght=wght),
            "e": Style(mutator, fs, wdth=1-e, wght=wght)},
            invisible_boundaries="/")
        .collapse()
        .remove_blanks()
        .align(f.a.r)
        .f(1))
    
    #print(pens.collapse().collapse().collapse().tree())

    if True:
        zoom = f.a.progress(f.i, loops=4, easefn="eeio")
        cidx = 3 - math.floor(zoom.loop/2)
        pe = zoom.e
        (pens.center_on_point(f.a.r, pens[cidx].bounds().point("C"), interp=pe)
            .scale(1+pe*2, point=pens[cidx].bounds().point("C")))

    return pens.insert(0, DP(f.a.r).f(0))

def release(passes):
    (FFMPEGExport(test_multi_var, passes, loops=2)
        .h264()
        .write()
        .open())