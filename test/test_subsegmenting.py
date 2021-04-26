from coldtype.test import *

f1 = Font.Cacheable("assets/ColdtypeObviously_BlackItalic.ufo")

@animation(timeline=Timeline(60))
def test_curves_only(f):
    e = f.a.progress(f.i, to1=1).e

    shape = (StyledString("C", Style(f1, 1000, wght=0.5))
        .pen()
        .align(f.a.r)
        .explode()[0])
    
    return (DPS([
        DATText(str(f.i), Style("Times", 30, load_font=0), f.a.r.inset(50)),
        (shape.copy().f(0, 0.1)),
        (shape.copy()
            .subsegment(0, e)
            .f(None).s(hsl(0.7, 1)).sw(3))]))
    
@animation(timeline=Timeline(60))
def test_mixed(f):
    e = f.a.progress(f.i, to1=1).e

    shape = (StyledString("D", Style(f1, 1000, wght=0.5))
        .pen()
        .align(f.a.r)
        .explode()[0]
        .fully_close_path())

    return (DPS([
        DATText(str(f.i), Style("Times", 30, load_font=0), f.a.r.inset(50)),
        (shape.copy().f(0, 0.1)),
        (shape.copy()
            .subsegment(0, e)
            .f(None).s(hsl(0.6, 1)).sw(3))]))