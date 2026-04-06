import math
from coldtype.beziers import CurveCutter, splitCubicAtT

try:
    import noise
except ImportError:
    raise Exception("`pip install noise`")

def warp_fn(xa=0, ya=-1, xs=300, ys=300, speed=5, base=0, octaves=1, mult=50, rz=1024):
    if ya == -1:
        ya = xa
    def warp(x, y):
        _x = (x+xa)/xs
        _y = (y+ya)/ys
        pn = noise.pnoise3(_x, _y, speed, octaves=octaves, base=base, repeatz=rz)
        return x+pn*mult, y+pn*mult
    return warp


def warp(flatten=10, xa=0, ya=-1, xs=300, ys=300, speed=5, base=0, octaves=1, mult=50, rz=1024):
    """Chainable function for warping a pen"""

    def _warp(pen):
        if flatten is not None and flatten > 0:
            pen.flatten(flatten)
        pen.nlt(warp_fn(xa, ya, xs, ys, speed, base, octaves, mult, rz))
    return _warp


def bend(pen, curve, tangent=True):
    def _bend(pen):
        cc = CurveCutter(curve)
        ccl = cc.length
        dpl = pen.bounds().point("SE").x
        xf = ccl/dpl

        def bender(x, y):
            p, tan = cc.subsegmentPoint(end=x*xf)
            px, py = p
            if tangent:
                a = math.sin(math.radians(180+tan)) * y
                b = math.cos(math.radians(180+tan)) * y
                return (px+a, py+b)
                #return (px, y+py)
            else:
                return (px, y+py)
        return pen.nonlinear_transform(bender)
    return _bend


def bend2(curve, tangent=True, offset=(0, 1)):
    def _bend(pen):
        bw = pen.bounds().w
        a = curve.value[0][-1][0]
        b, c, d = curve.value[1][-1]
        def bender(x, y):
            c1, c2 = splitCubicAtT(a, b, c, d, offset[0] + (x/bw)*offset[1])
            _, _a, _b, _c = c1
            if tangent:
                tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
                ax = math.sin(math.radians(90-tan)) * y
                by = math.cos(math.radians(90-tan)) * y
                return _c[0]+ax, (y+_c[1])+by
            return _c[0], y+_c[1]
        return pen.nonlinear_transform(bender)
    return _bend


def bend3(curve, tangent=False, offset=(0, 1)):
    def _bend(pen):
        a = curve.value[0][-1][0]
        b, c, d = curve.value[1][-1]
        bh = pen.bounds().h
        
        def bender(x, y):
            c1, c2 = splitCubicAtT(a, b, c, d, offset[0] + (y/bh)*offset[1])
            _, _a, _b, _c = c1
            if tangent:
                tan = math.degrees(math.atan2(_c[1] - _b[1], _c[0] - _b[0]) + math.pi*.5)
                ax = math.sin(math.radians(90-tan)) * y
                by = math.cos(math.radians(90-tan)) * y
                return x+_c[0]+ax, (y+_c[1])+by
            return x+_c[0], _c[1]
        return pen.nonlinear_transform(bender)
    return _bend