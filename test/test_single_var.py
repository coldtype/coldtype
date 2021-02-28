from coldtype.test import *

tl = Timeline(60, fps=30)

@animation((1600, 600), timeline=tl)
def test_multi_var(f):
    e = f.a.progress(f.i, loops=1, easefn="eeio").e
    e2 = f.a.progress(f.i, loops=2, easefn="eei").e
    fs = 200

    wght = (1-e)*0.25

    pens = (RichText(f.a.r, "T[t] Y[y] P[p] E[e]", {
            "t": Style(mutator, fs, wdth=e, wght=wght),
            "y": Style(mutator, fs, wdth=1-e2, wght=wght),
            "p": Style(mutator, fs, wdth=e2, wght=wght),
            "e": Style(mutator, fs, wdth=1-e, wght=wght)})
        .collapse()
        .remove_blanks()
        .track(40)
        .align(f.a.r)
        .f(0))

    cidx = 2 # the Y
    return (pens
        .center_on_point(f.a.r, pens[cidx].bounds().point("C"), interp=e)
        .scale(1+e*2, point=pens[cidx].bounds().point("C"))
        .insert(0, DP(f.a.r).f(1)))

def release(passes):
    (FFMPEGExport(test_multi_var, passes, loops=4)
        .h264()
        .write()
        .open())