from coldtype import *

irr = Font.Cacheable("~/Type/fonts/fonts/IrregardlessVariable.ttf")

@animation((1920, 1080), timeline=Timeline(60))
def irregardless(f):
    e = f.a.progress(f.i, loops=1, easefn="ceio").e
    return (StSt("Irregardless", irr, 400,
        wght=e, slnt=(1-e), tu=100+(1-e)*-330, rotate=360*e, ro=1)
        .pens()
        .align(f.a.r)
        .f(hsl(0.7, a=0.75))
        .s(0).sw(5))