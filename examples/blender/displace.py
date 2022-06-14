from coldtype import *
from coldtype.blender import *

@b3d_runnable()
def setup(bw:BpyWorld):
    bw.deletePrevious(materials=False)

@b3d_renderable(center=(0, 1), upright=1, reset_to_zero=1)
def bg(r):
    return (P(r)
        .tag("bg")
        .ch(b3d(lambda p: p
            .extrude(0.1)
            , material="bg_mat")))

@b3d_renderable(center=(0, 1), upright=1)
def displace(r):
    return (
        #StSt("S", "OhnoSoftieVariable.ttf", 850, wdth=1, wght=1)
        #.align(r)
        #.pen()
        P().rect(r.inset(300))
        .tag("glyph")
        .ch(b3d(lambda p: p
            .extrude(1)
            .convertToMesh()
            .remesh(7)
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
            .smooth(factor=5, repeat=2, x=0, y=0, z=1)
            .shadeSmooth()
            , material="sponge")))

@b3d_animation(tl=60)
def animator(f):
    (BpyObj.Find("bg")
        .locate(y=f.e("seo", 1, r=(1, -2.95))))
    (BpyObj.Find("glyph_EmptyOrigin")
        .rotate(z=f.e("l", 0, r=(0, 360))))

@b3d_runnable(delay=True)
def post_setup(bw:BpyWorld):
    bw.scene.frame_set(20)