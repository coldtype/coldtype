from coldtype import *
from coldtype.blender import *

peshka = Font.Cacheable("~/Type/fonts/fonts/CoFoPeshkaVariableV0.6.ttf")

def ts(f, x):
    return (StSt("DEPTH\nOF\nFIELD", peshka,
        f.adj(-x).e("eeio", 1, rng=(350, 150)),
        wdth=f.adj(-x).e("eeio", 2),
        wght=f.adj(-x).e("seio", 3),
        ro=1
        )
        .pen()
        .tag(f"ts_{x}")
        .align(f.a.r)
        #.translate(0, f.adj(-x).e("eeio", 2, rng=(50, -50)))
        .q2c()
        .ch(b3d("Text", lambda bp: bp
            .extrude(0.1)
            .rotate(90)
            .locate(0, x*0.25+x*f.e("eeio", 1, rng=(0, 1.5)), 0))))

@b3d_animation(timeline=240, rstate=1)
def var3d2(f, rs):
    if bpy:
        bpy.data.cameras["Camera"].dof.aperture_fstop = f.e("eeio", 2, rng=(7, 2.5))
        bpy.data.objects["Empty"].location[2] = f.e("seio", 1, rng=(7, 5))

    out = DPS()
    for x in range(0, 40 if bpy else 1):
        out.insert(0, ts(f, x))

    return out

def _release(artifacts):
    for a in artifacts[:]:
        fi = a.args[0].i
        print(">", fi)
        var3d2.blender_render_frame(__FILE__, "examples/blender/3dvar.blend", fi, samples=32)

def build(artifacts):
    _release(artifacts[0:1])

def release(artifacts):
    _release(artifacts[232:])