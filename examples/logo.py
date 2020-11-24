from coldtype import *
from coldtype.midi.controllers import LaunchControlXL

obv = Font.Cacheable("assets/ColdtypeObviously-VF.ttf")

@renderable(rstate=1)
def logo(r, rs):
    nxl = LaunchControlXL(rs.midi)
    word = (StyledString("COLDTYPE",
        Style(obv, 725, wdth=0, tu=-50, r=1))
        .pens()
        .f(1)
        .align(r, th=1, tv=1)
        .rotate(15)
        .translate(-10, 5)
        .understroke(sw=25)
        
        .f(1))
    
    return DATPenSet([
        DATPen().rect(r).f(hsl(0.6, s=1, l=0.25)).f(1),
        # word.copy().phototype(SkiaPen, r,
        #     blur=25,
        #     cut=150,
        #     cutw=150,
        #     fill=hsl(0.91, s=1, l=0.6),
        #     context=__CONTEXT__),
        word.copy().phototype(SkiaPen, r,
            blur=2+10*nxl(10),
            cut=50+200*nxl(20),
            cutw=1+10*nxl(30),
            trace=0,
            fill=bw(0),
            context=__CONTEXT__)
    ])
    return 