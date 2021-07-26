from coldtype import *
from coldtype.blender import *
import math

fnt = Font.Find("NaNJauneMaxi")

@b3d_animation(
    timeline=240,
    blender_file="examples/blender/geometry2.blend")
def jaune(f):
    if bpy:
        bpy.data.objects["Camera.002"].location[2] = f.e("eeio", 1, rng=(5.4, 9))
        bpy.data.objects["Camera.002"].rotation_euler[0] = math.radians(f.e("eeio", 1, rng=(90, 83)))

    rect = f.a.r.inset(500)
    def layer(i, x):
        wght = f.adj(-x*3).e("eeio", 2)
        return (StSt("Var", fnt, 500,
            wght=wght, grvt=wght, ro=1)
            .align(rect)
            .fssw(None, hsl(0.65), 2)
            .pen()
            .tag(f"l{x}")
            .outline(2)
            .ch(b3d_mod(lambda p: p
                .fssw(hsl(0.23, 1, 0.6), None, None)
                .f(hsl(f.adj(-x*5).e("seio", 1)))))
            .ch(b3d("Text", lambda bp: bp
                .extrude(0.01)
                .rotate(90)
                .roughness(1)
                .transmission(0)
                .locate(0, x*5, 0))))

    return DPS.Enumerate(range(0, 10), layer)

build, release = jaune.build_release()