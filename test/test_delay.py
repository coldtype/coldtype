from coldtype import *

co = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@animation((1500, 800), timeline=Timeline(60, fps=23.976))
def var(f, depth=0):
    t = f.a.progress(f.i, loops=1, easefn="qeio") 
    cold = (StyledString("COLDTYPE",
        Style(co, 800-t.e*700, wdth=t.e, ro=1, tu=-90+t.e*50, r=1))
        .pens()
        .align(f.a.r)
        .f(None)
        .understroke()
        .s(1).sw(15-depth*0.65))
    
    if depth < 20:
        cold.insert(0, var.func(Frame((f.i-1)%var.duration, f.a, []), depth=depth+1))
    
    if depth == 0:
        return DATPenSet([
            DATPen().rect(f.a.r).f(1),
            cold.phototype(f.a.r, cut=200, cutw=10, fill=bw(0))])
    else:
        return cold