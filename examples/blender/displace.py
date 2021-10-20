from coldtype import *
from coldtype.blender import *

@b3d_renderable(center=(0, 1), upright=1)
def scratch(r):
    return (Glyphwise("CHEEESE", lambda g:
        Style(Font.Find("Cheee-V"), 350,
            yest=1-g.e,
            grvt=1-g.e,
            temp=g.e))
        .align(r)
        .pen()
        .tag("glyph")
        .ch(b3d(lambda bp: bp
            .extrude(1)
            .convert_to_mesh()
            .remesh(7)
            .apply_modifier("Remesh")
            .make_vertex_group(lambda v: v.co[2] > 0)
            .displace(
                strength=0.5,
                midlevel=0,
                texture="Texture",
                coords_object="Empty",
                direction="Z",
                vertex_group="Group")
            .subsurface()
            .smooth(factor=5, repeat=2, x=0, y=0, z=1)
            .shade_smooth()
            , dn=1
            , material="sponge"
            , upright=1)))