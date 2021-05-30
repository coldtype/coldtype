from coldtype.test import *


@test()
def test_fit(r):
    inset = 150
    return [
        DATPen().rect(r.inset(inset, 0)).f("hr", 0.5, 0.9),
        Slug("COLD", Style(co, 500, wdth=1, wght=1, slnt=1, tu=-150, r=1)).fit(r.w-inset*2).pens().f("random").align(r).understroke()
    ]


@test()
def test_style_mod(r):
    style = Style(co, 250, wdth=1)
    out = DATPens()
    out += StyledString("CLDTP", style).pen()
    out += StyledString("CLDTP", style.mod(wdth=0)).pen()
    return out.rp().distribute(v=1).track(10, v=1).align(r).f("hr", 0.5, 0.5)


@test()
def test_fit_height(r):
    style = Style(co, 150, wdth=1)
    out = DATPens()
    out += StyledString("CLDTP", style).pen()
    out += StyledString("CLDTP", style.mod(fitHeight=300)).pen()
    return out.rp().distribute(v=1).track(10, v=1).align(r).f("hr", 0.5, 0.5)


@test()
def test_interp(r):
    count = 30
    out = DATPens()
    for x in range(count):
        style = Style(co, 200, wdth=x/count, ro=1)
        out += StyledString("COLDTYPE", style).pens().f("random", 0.1).s(0, 0.1).sw(2).align(r).translate(0, x).rotate(x*0.5)
    return out


@test()
def test_kern_pairs(r):
    return (StyledString("CLD",
        Style(co, 300, rotate=-10, kp={"C/L":20, "L/D":45}))
        .pens()
        .align(r).f("hr", 0.65, 0.65))