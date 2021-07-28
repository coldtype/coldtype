from coldtype import *
from coldtype.blender import *

peshka = Font.Find("PeshkaVariableV0.6")

@b3d_animation(timeline=240)
def var3d2(f):
    if bpy:
        bpy.data.cameras["Camera"].dof.aperture_fstop = f.e("eeio", 2, rng=(7, 2.5))
        bpy.data.objects["Empty"].location[2] = f.e("seio", 1, rng=(7, 5))
    
    return (DPS.Enumerate(range(0, 10 if bpy else 1), lambda i,x:
        (StSt("DEPTH\nOF\nFIELD", peshka,
            f.adj(-x).e("eeio", 1, rng=(350, 150)),
            wdth=f.adj(-x).e("eeio", 2),
            wght=f.adj(-x).e("seio", 3),
            ro=1)
            .pen()
            .tag(f"ts_{x}")
            .align(f.a.r)
            .q2c()
            .ch(b3d("Text", lambda bp: bp
                .extrude(0.1)
                .rotate(90)
                .locate(0, x*0.25+x*f.e("eeio", 1, rng=(0, 1.5)), 0))))))