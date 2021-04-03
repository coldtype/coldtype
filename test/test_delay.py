from coldtype import *
from coldtype.warping import warp_fn

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation((1500, 800), timeline=Timeline(60, fps=23.976))
def var(f, depth=0):
    t = f.a.progress(f.i, loops=1, easefn="qeio") 
    cold = (StyledString("COLDTYPE",
        Style(co, 800-t.e*700, wdth=t.e, ro=1, tu=-90+t.e*50, r=1))
        .pens()
        .align(f.a.r)
        .f(1)
        .s(0)
        .sw(23-depth)
        .pmap(lambda i, p: p.nlt(warp_fn(0, 0, mult=30))))
    
    cold = (cold
        .color_phototype(f.a.r, blur=2+depth*5, cut=120+depth*5, rgba=[1, 0, 1, 1])
        .ups()
        .blendmode(skia.BlendMode.kDifference))
    
    if depth < 5:
        cold.insert(0, var.func(Frame((f.i-3)%var.duration, f.a), depth=depth+1))
    
    if depth == 0:
        return DATPens([
            #DATPen().rect(f.a.r).f(1),
            cold.color_phototype(f.a.r, blur=5)])
    else:
        return cold