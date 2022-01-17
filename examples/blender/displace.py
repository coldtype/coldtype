from coldtype import *
from coldtype.blender import *

@b3d_renderable(center=(0, 1), upright=1)
def displace(r):
    return (StSt("ABC", Font.MutatorSans(), 350
        , wdth=0, wght=1)
        .align(r)
        .pen()
        .tag("glyph")
        .ch(b3d(lambda p: p.extrude(1)
            .convertToMesh()
            .remesh(7)
            .applyModifier("Remesh")
            .makeVertexGroup(lambda p: p.co[2] > 0, name="front")
            .displace(
                strength=0.85,
                midlevel=1,
                texture="Texture",
                coords_object="Empty",
                direction="Z",
                vertex_group="front")
            .subsurface()
            .smooth(factor=5, repeat=2, x=0, y=0, z=1)
            .shadeSmooth()
            , dn=1
            , material="sponge"
            , upright=1)))