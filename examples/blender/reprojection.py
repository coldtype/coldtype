from coldtype import *
from coldtype.blender import *

"""
a 2d coldtype variable font animation;
in the same file as @b3d_runnable that
displays that 2d animation in a 3d world
"""

# to fully re-cache Rendered sequence in blender, make sure to set force_refresh=1 on your @b3d_runnable

@animation((540, 540), timeline=30)
def varfont_animation(f):
    return (P(
        Glyphwise("COLD", lambda g:
            Style(Font.ColdObvi(), 250
                , wdth=f.adj(-g.i*40).e("seio")))
            .align(f.a.r, tx=0)
            .f(hsl(0.3)),
        StSt(str(f.i)
            , Font.JBMono(), 50)
            .align(f.a.r.inset(50), tx=0, y="S")
            .f(0)))

@b3d_runnable(force_refresh=1)
def setup(blw:BpyWorld):
    blw.delete_previous(materials=False)

    (BpyObj.Plane("Projection")
        .scale(2, 2)
        .material("projection_material", lambda m: m
            .f(0)
            .specular(0)
            .animation(varfont_animation)))