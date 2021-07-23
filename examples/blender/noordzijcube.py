from coldtype import *
from coldtype.blender import *

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

d = 5

def entry(f, i, g, x, y, z):
    return (StSt("E", fnt, 250, ro=1,
        wght=x/(d-1),
        wdth=(y/(d-1)),
        slnt=(z/(d-1)))
        .pen()
        .f(None).s(0).sw(1)
        .f(1)
        .align(g)
        .tag(f"{x}{y}{z}")
        .ch(b3d_mod(lambda p: p
            .f(1).s(None).sw(0)))
        .ch(b3d("Cube", lambda bp: (bp
            .extrude(0.1+x/(d-1)*0.1)
            .rotate(90)
            .locate(-5.4, -5.4 + 10.8*(z/d), 0)))))

@b3d_animation(timeline=120)
def cube(f):
    gs = f.a.r.grid(d, d)
    out = DPS()
    gi = 0
    gs = gs * d
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
                out += entry(f, gi, gs[gi], x, y, z)
                gi += 1
    return out

def _release(artifacts):
    for a in artifacts[:]:
        fi = a.args[0].i
        print(">", fi)
        cube.blender_render_frame(__FILE__, "examples/blender/noordzijcube.blend", fi, samples=16)

def build(artifacts):
    _release([artifacts[60]])

def release(artifacts):
    _release(artifacts[:])