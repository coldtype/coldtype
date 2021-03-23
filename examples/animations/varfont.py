from coldtype import *

font1 = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")
font2 = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

tl = Timeline(30, fps=30)

@animation(bg=0, timeline=tl)
def stub(f):
    e1 = f.a.progress(f.i, easefn="linear").e
    e2 = f.a.progress(f.i, loops=1, easefn="eeio").e
    e3 = f.a.progress(f.i, loops=1, easefn="qeio").e
    
    a, b = f.a.r.inset(0, 240).subdivide(2, "mxy")

    programming = (StyledString("Programming",
        Style(font2, 200-e2*50,
            #wdth=0.3, wght=1-e2*0.5, slnt=1,
            #tu=-100+200*e2,
            r=1,
            rotate=e2*10,
            ))
        .pens()
        #.f(1)
        #.understroke(sw=13)
        #.align(a)
        )

    design = (StyledString("Design",
        Style(font1, 310,
            #grvt=e2,
            #yest=0.37,
            #tu=-90,
            r=1))
        .pens()
        #.f(1)
        #.understroke(sw=20)
        #.align(b)
        )

    return (DPS([
            programming,
            design
        ])
        #.phototype(f.a.r, blur=3, cut=180, cutw=30, fill=hsl(e1, s=1, l=0.7))
        )