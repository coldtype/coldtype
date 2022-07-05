from coldtype import *
from coldtype.blender import *

# to fully re-cache Rendered sequence in blender, try switching to Material Preview and then back to Rendered

@animation((540, 540), timeline=30, bg=0)
def varfont_animation(f):
    return (P(
        Glyphwise("CDEL", lambda g:
            Style(Font.ColdObvi(), 250
                , wdth=f.adj(-g.i*40).e("seio")))
            .align(f.a.r, th=0)
            .f(1),
        StSt(str(f.i)
            , Font.RecursiveMono(), 50)
            .align(f.a.r.inset(50), th=0, y="S")
            .f(1)))

@b3d_runnable()
def setup(blw:BpyWorld):
    (blw.deletePrevious(materials=False))

    (BpyObj.Plane("Projection")
        .scale(2, 2)
        .material("projection_material", lambda m: m
            .f(0)
            .specular(0)
            .animation(varfont_animation)))