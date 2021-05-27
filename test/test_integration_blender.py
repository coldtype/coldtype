from coldtype import *
from coldtype.integrations.blender import BlenderRenderConfig

brc = BlenderRenderConfig(
    __sibling__("test_media/_test.blend"),
    __sibling__("test_media/_blender_renders"))

fnt = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@animation(bg=0)
def test_blender(f):
    out = (StSt(str(f.i), fnt, 1000, wdth=1)
        .pen()
        .align(f.a.r, tv=1)
        .f(hsl(0.7, 1))
        .add_data("blenderpen", dict(extrude=[3]))
        .chain(brc.blend_fn(0, skip=0))
        )
    return out
