from coldtype import *
from coldtype.timing.easing import applyRange

def keyalign(self:P, frame, r, align="C"):
    if not hasattr(self, "_keyframes_align"):
        self._keyframes_align = []
    self._keyframes_align.append([frame, r, align])
    return self

def calc_keyalign(self:P, fi, ease="eeio"):
    ks = sorted(self._keyframes_align, key=lambda x: x[0])
    a = None
    b = None
    for kidx, (k, r, align) in enumerate(ks):
        if fi == k:
            return self.align(r, align)
        if fi > k:
            a = [k, r, align]
            b = ks[kidx+1]
    
    if a and b:
        diff = ez((fi - a[0]) / (b[0] - a[0]), ease)
        self.align(a[1].r.interp(diff, b[1].r), a[2])
    return self

def keyrotate(self:P, frame, r, pt="C"):
    if not hasattr(self, "_keyframes_rotate"):
        self._keyframes_rotate = []
    self._keyframes_rotate.append([frame, r, pt])
    return self

def calc_keyrotate(self:P, fi, ease="eeio"):
    ks = sorted(self._keyframes_rotate, key=lambda x: x[0])
    a = None
    b = None
    for kidx, (k, r, pt) in enumerate(ks):
        if fi == k:
            return self.rotate(r, pt)
        if fi > k:
            a = [k, r, pt]
            b = ks[kidx+1]
    
    if a and b:
        diff = ez((fi - a[0]) / (b[0] - a[0]), ease)
        _r = applyRange(diff, rng=(a[1], b[1]))
        self.rotate(_r, a[2])
    return self

P.keyalign = keyalign
P.calc_keyalign = calc_keyalign
P.keyrotate = keyrotate
P.calc_keyrotate = calc_keyrotate

@animation(Rect(1000), tl=Timeline(60))
def scratch(f):
    s = Scaffold(f.a.r).labeled_grid(4, 4)
    return (P(
        s.borders(),
        P().rect(Rect(200))
        #StSt("ABC", Font.JBMono(), 50)
            .f(0).pen()
            .keyalign(0, s["a0"])
            .keyalign(24, s["d2"])
            .keyalign(35, s["c0"])
            .keyalign(50, s["b3"])
            .keyalign(59, s["a0"])
            .keyrotate(0, 0)
            .keyrotate(24, 180)
            .keyrotate(59, 360)
            .calc_keyalign(f.i, "eeio")
            .calc_keyrotate(f.i, "eeio"),
        ))