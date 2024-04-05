from coldtype import *
from coldtype.blender import *

"""
A variable font animation that works in 2D and 3D;
also a little bit of camera manipulation in here
to dynamically adjust depth-of-field in coordination
with the letters’ movement
"""

rs1 = random_series(-5, 5)

@b3d_animation(timeline=180, upright=1)
def var3d2(f):
    if bpy and bpy.data:
        bpy.data.cameras["Camera"].dof.aperture_fstop = f.e("ceio", 1, rng=(0.1, 0.01))
    
    return (StSt("DEPTH\nOF\nFIELD", Font.MutatorSans()
        , fontSize=f.e("eeio", 2, rng=(150, 100))
        , wdth=f.e("eeio", 1)
        , wght=f.e("ceio", 4)
        , leading=30
        , ro=1)
        .xalign(f.a.r)
        .align(f.a.r)
        .collapse()
        .mapv(lambda i, p: p
            .tag(f"glyph_{i}")
            .ch(b3d(lambda bp: bp
                .extrude(0.1)
                .locate(
                    x=0,
                    y=rs1[i]*f.e("eeio", 2, rng=(0, 1.5)) if i != 5 else 0,
                    z=0)))))