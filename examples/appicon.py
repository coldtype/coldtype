from coldtype import *

co = Font("assets/ColdtypeObviously-VF.ttf")

c1 = hsl(0.65, 0.7)
c2 = hsl(0.53, 0.6)

@iconset(rect=(1024, 1024), sizes=(1024,))
def appicon(r, size):
    grade = Gradient.Horizontal(r, c1, c2)
    outline = 15
    if size <= 128:
        st = Style(co, 1000, wdth=0.5, r=1, t=50, rotate=15)
        return (StyledString("CT", st)
            .pens()
            .align(r)
            .f(grade)
            .understroke(s=1, sw=50))
    else:
        def st(tu):
            return Style(co, 500,
                tu=tu, wdth=0.7, rotate=15,
                kp={"P/E": (-150, 0)}, r=1)
        
        return (DATPens([
            (StyledString("COLD", st(-70))
                .pens()
                .align(r.take(0.5, "mxy"))
                .translate(0, -150)),
            (StyledString("TYPE", st(-50))
                .pens().align(r.take(0.5, "mny")))])
            .f(grade)
            .reversePens()
            .understroke(s=1, sw=10)
            .align(r))