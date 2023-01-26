from coldtype import *
from coldtype.blender import *

@b3d_runnable()
def setup(bw:BpyWorld):
    (bw.deletePrevious(materials=False))

big_c = "A"

@b3d_renderable(center=(0, 1), upright=1)
def displace(r):
    return (
        StSt("C", Font.ColdObvi(), 850, wght=1)
        .align(r)
        .pen()
        .tag("glyph")
        .ch(b3d(lambda p: p
            .extrude(1)
            .convertToMesh()
            .remesh(6)
            .applyModifier("Remesh")
            .makeVertexGroup(lambda p: p.co[2] > 0, name="front")
            .addEmptyOrigin()
            .displace(
                strength=3.35,
                midlevel=0,
                texture="Texture",
                coords_object="glyph_EmptyOrigin",
                direction="Z",
                vertex_group="front")
            .subsurface()
            .smooth(factor=6, repeat=2, x=0, y=0, z=1)
            .shadeSmooth()
            , material="sponge")))

@b3d_animation(tl=30, name=f"animator_{big_c}")
def animator(f):
    # (BpyObj.Find("bg")
    #     .locate(y=f.e("seo", 1, r=(1, -2.95))))
    if bpy and bpy.data:
        (BpyObj.Find("glyph_EmptyOrigin")
            .locate(x=ord(big_c)+f.e("l", 0, r=(0, 2)))
            .rotate(x=f.e("l", 0, r=(0, 5))))

@b3d_runnable(delay=True)
def post_setup(bw:BpyWorld):
    bw.scene.frame_set(20)