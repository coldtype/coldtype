from coldtype import *
from coldtype.blender import *

"""
A giant letter, w/ the top face displaced
with a Displace modifier; then animated
by moving the Displace modifier's coords
object w/ a @b3d_animation
"""

big_c = "C"

@b3d_runnable()
def setup(bw:BpyWorld):
    (bw.deletePrevious(materials=True))

    glyph = (StSt(big_c, Font.ColdObvi(), 8.5, wght=1)
        .pen()
        .shift(-0.5, 0.5))
    
    (BpyObj.Curve("Glyph")
        .draw(glyph)
        .extrude(1)
        .origin_to_cursor()
        .rotate(x=90)
        .convert_to_mesh()
        .remesh(6)
        .apply_modifier("Remesh")
        .make_vertex_group(lambda p: p.co[2] > 0, name="front")
        .add_empty_origin()
        .displace(
            strength=3.35,
            midlevel=0,
            texture="Texture",
            coords_object="Glyph_EmptyOrigin",
            direction="Z",
            vertex_group="front")
        .subsurface()
        .smooth(factor=6, repeat=2, x=0, y=0, z=1)
        .shade_smooth()
        .material("sponge", lambda m: m
            .f(hsl(0.65))))

@b3d_animation(tl=30, name=f"animator_{big_c}")
def animator(f):
    if bpy and bpy.data:
        (BpyObj.Find("Glyph_EmptyOrigin")
            .locate(x=ord(big_c)+f.e("l", 0, r=(0, 2)))
            .rotate(x=f.e("l", 0, r=(0, 5))))

@b3d_runnable(delay=True)
def post_setup(bw:BpyWorld):
    bw.scene.frame_set(20)