from coldtype import *
from coldtype.fx.skia import phototype

r = Rect(1080, 540)
font = Font.ColdObvi()

def shapes(r):
    return (StSt("COLD", font, 250)
        .align(r))

@renderable(r)
def graphic(r):
    return P(r).f(0) + (shapes(r).f(1))

from coldtype.blender import *

@b3d_runnable()
def setup(blw:BpyWorld):
    (blw.deletePrevious(materials=False)
        .timeline(Timeline(50, 12)
            , output=__FILE__
            , version=1))

    (BpyObj.Plane("ImagePlane")
        .scale(2, 1)
        .material("asdf_image", lambda m: m
            .image(graphic.pass_path())))

#bpy.data.materials["asdf_image"].node_tree.nodes["Mapping.001"].inputs[1].default_value[0]