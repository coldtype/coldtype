from coldtype import *
from coldtype.blender import *

r = Rect(1080, 540)
font = Font.ColdObvi()

@renderable(r, bg=0, render_bg=1)
def graphic(r):
    return (StSt("TYPE", font, 250)
        .f(1)
        .align(r))

@b3d_runnable(force_refresh=True)
def setup(blw:BpyWorld):
    (blw.delete_previous(materials=False)
        .timeline(Timeline(50, 12)
            , output=__FILE__
            , version=1))

    (BpyObj.Plane("ImagePlane")
        .scale(2, 1)
        .material("asdf_image", lambda m: m
            .image(graphic, emission=0, render=True)))