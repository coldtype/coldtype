from coldtype.test import *

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

def bend3(self, curve, tangent=True):
    from coldtype.beziers import CurveCutter, splitCubicAtT
    cc = CurveCutter(curve)
    ccl = cc.length
    mnx = curve.bounds().point("SW").x
    dpl = self.bounds().point("SE").x
    bh = self.bounds().h
    xf = ccl/dpl
    a = curve.value[0][-1][0]
    b, c, d = curve.value[-1][-1]
    def bender(x, y):
        c1, c2 = splitCubicAtT(a, b, c, d, y/bh)
        _, _a, _b, _c = c1
        if tangent:
            tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
            ax = math.sin(math.radians(tan)) * y
            by = math.cos(math.radians(tan)) * y
            return x+_c[0]+ax, (y+_c[1])+by
        #return x, y
        return x+_c[0], y+_c[1]/2
    return self.nonlinear_transform(bender)

DATPen.bend3 = bend3

@test(rstate=1)
def test_text_warped_to_curve(r, rs):
    text:DATPenSet = (StyledString("WARPTOUR",
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
            .scale(0.5, center=r.point("C"))),
        (text.pen().s(0.7)),
        (text.pen()
            .flatten(5)
            .bend2(sine, tangent=1)
            .scale(0.5, center=r.point("C")))]

@test((1000, 1000), solo=1, rstate=1)
def test_text_warped_to_vertical_curve(r, rs):
    text:DATPenSet = (StyledString("COLDTYPE",
        Style(co, 600, tu=-10, r=1, ro=1, wdth=0.25))
        .pens()
        .f(None)
        .s(0)
        .sw(2))

    r = r.inset(0, 0)
    sine = (DATPen()
        .moveTo((r.x, r.y))
        .curveTo(
            rs.mouse.offset(0, -100) if rs.mouse else (r.x+300, r.y+150),
            rs.mouse.offset(0, 100) if rs.mouse else (r.x+300, r.y+r.h-150),
            (r.x, r.y+r.h)))
    
    return (DATPenSet([
        (sine.copy()
            .f(None)
            .s(hsl(0.9))
            .sw(3)),
        ßhide(text.pen().s(0.7)),
        (text.pen()
            .flatten(5)
            .translate(0, 0)
            .bend3(sine, tangent=0))])
        .scale(0.35, center=r.point("C"))
        .translate(-200, 0))

@test((1000, 1000))
def test_text_on_a_curve_fit(r):
    circle = DATPen().oval(r.inset(250)).reverse()
    return (StyledString("COLDTYPE COLDTYPE COLDTYPE ",
        Style(co, 100, wdth=1, tu=0, space=500))
        .fit(circle.length())
        .pens()
        .distributeOnPath(circle)
        .f(Gradient.H(circle.bounds(), hsl(0.5, s=0.6), hsl(0.85, s=0.6))))