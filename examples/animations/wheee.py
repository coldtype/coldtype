from coldtype import *

# keyboard shortcut backslash to clear visual buffer

@animation((1080, 1080), timeline=120, bg=0, composites=1)
def wheee(f):
    return P(
        f.last_render(lambda img: img.rotate(0)),
        (StSt("TYPE", Font.MuSan(), f.e("qeio", 1, r=(210, 70))
            , wdth=f.e("qeio", r=(1, 0))
            , wght=f.e("qeio"))
            .align(f.a.r)
            .rotate(f.e("l", 2, cyclic=0, r=(0, 360)))
            .fssw(hsl(f.e("l", 2, cyclic=0), s=0.6), 0, 4, 1)))