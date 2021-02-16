from coldtype.test import *
from importlib import reload

@test()
def test_text_on_a_curve(r):
    return (StyledString("COLDTYPE "*7,
        Style(co, 64, tu=-50, r=1, ro=1))
        .pens()
        .pmap(lambda i, p: p.f(hsl(0.3+random()*0.3, l=0.7)))
        .distribute_on_path(DATPen()
            .oval(r.inset(50))
            .reverse()
            .repeat())
        .understroke(s=0, sw=5))

@test(rstate=1, solo=0, watch_restarts=["coldtype/pens/datpen.py"])
def test_text_warped_to_curve(r, rs):
    text:DATPens = (StyledString("WARPTOUR",
        Style(mutator, 164, tu=-250, r=1, ro=1, wght=1))
        .pens()
        .f(None)
        .s(0)
        .sw(2))

    r = r.inset(0, 100).offset(0, -50)
    sine = (DATPen()
        .moveTo((r.x, r.y))
        .curveTo(
            rs.mouse if rs.mouse else (r.w/2, r.y-100),
            (r.x+r.w-r.w/2, r.y+r.h+100),
            (r.x+r.w, r.y+r.h)))
    
    return [
        (sine.copy()
            .f(None)
            .s(hsl(0.9))
            .sw(3)
            .scale(0.5, point=r.point("C"))),
        #(text.pen().s(0.7)),
        (text.pen()
            .flatten(10)
            #.scale(1, 2)
            .bend2(sine, tangent=0, offset=[-1, 2])
            .scale(0.5, point=r.point("C")))]

@test((1000, 1000), solo=1, rstate=1, watch_restarts=["coldtype/pens/datpen.py"])
def test_text_warped_to_vertical_curve(r, rs):
    text:DATPens = (StyledString("COLDTYPE",
        Style(co, 600, tu=-10, r=1, ro=1, wdth=0))
        .pens()
        .f(None)
        .s(0)
        .sw(2))
    
    #text = DATPen().rect(Rect(0, 0, 100, 500)).f(None).s(0)

    r = r.take(0.5, "mny")
    sine = (DATPen()
        .moveTo((r.x, r.y))
        .curveTo(
            rs.mouse.offset(0, -100) if rs.mouse else (r.x+300, r.y+150),
            rs.mouse.offset(0, 100) if rs.mouse else (r.x+300, r.y+r.h-150),
            (r.x, r.y+r.h)))
    
    return (DATPens([
        (sine.copy()
            .f(None)
            .s(hsl(0.9))
            .sw(3)),
        #text.pen().s(0.7),
        (text.pen()
            .flatten(10)
            .translate(0, 0)
            .bend3(sine, tangent=1, offset=[0, 1]))
            .f(hsl(0.9, a=0.3))])
        .scale(0.5, point=r.point("C"))
        .translate(50, 200))

@test((1000, 1000))
def test_text_on_a_curve_fit(r):
    circle = DATPen().oval(r.inset(250)).reverse()
    return (StyledString("COLDTYPE COLDTYPE COLDTYPE ",
        Style(co, 100, wdth=1, tu=0, space=500))
        .fit(circle.length())
        .pens()
        .distributeOnPath(circle)
        .f(Gradient.H(circle.bounds(), hsl(0.5, s=0.6), hsl(0.85, s=0.6))))