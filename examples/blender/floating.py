from coldtype import *
from coldtype.blender import *
from noise import pnoise1

tilda = Font.Cacheable("~/Type/fonts/fonts/Tilda Grande.otf")

@b3d_animation(timeline=240)
def floating(f):
    def square(x):
        return (DP()
            .record(StSt("Floating",
                tilda, 500,
                wght=f.adj(-x*2)
                    .e("seio", 2, rng=(0, 0.95)))
                .align(f.a.r, tv=1, th=1))
            .f(hsl(0.75, 0.6))
            .tag(f"square{x}")
            .ch(b3d("Geometry", lambda bp: bp
                .extrude(0.55)
                .transmission(0)
                .roughness(1)
                .rotate(90)
                .locate(0, x*7,
                    -.5+pnoise1(2+f.adj(-x*5)
                        .e("l")*5)*5.5))))
    
    return DPS.Enumerate(range(0, 10),
        lambda _, x: square(x))

def _release(artifacts):
    for a in artifacts[:]:
        fi = a.args[0].i
        floating.blender_render_frame(__FILE__, "examples/blender/floating.blend", fi, samples=32)

def build(artifacts):
    _release(artifacts[0:1])

def release(artifacts):
    _release(artifacts[:])