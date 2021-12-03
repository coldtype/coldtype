from coldtype import *
from coldtype.fx.skia import color_phototype


@animation((1500, 800), timeline=Timeline(60, fps=23.976))
def recur(f, depth=0):
    t = f.a.progress(f.i, loops=1, easefn="qeio") 
    cold = (StSt("COLDTYPE", Font.ColdObvi()
            , fontSize=800-t.e*700
            , wdth=t.e
            , tu=-90+t.e*50
            , ro=1
            , r=1)
        .align(f.a.r)
        .fssw(1, 0, 23-depth)
        .ch(color_phototype(f.a.r, blur=2+depth*5, cut=120+depth*5, rgba=[1, 0, 1, 1]))
        .ups()
        .blendmode(BlendMode.Luminosity))
    
    if depth < 5:
        cold.insert(0,
            recur.func(Frame((f.i-4)%recur.duration, f.a)
                , depth=depth+1))
    
    if depth == 0:
        return cold.ch(color_phototype(f.a.r, blur=3))
    else:
        return cold