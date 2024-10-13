from coldtype import *
from coldtype.blender import *

@animation((1080, 1080), timeline=360, solo=1)
def varfont_animation_overlay(f):
    ease_curve = P().withRect(1000, lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pne, 19, 10))
    
    return (P(
        Glyphwise("PARCH", lambda g:
            Style("ParchVF", 50, DCAY=f.adj(g.i*10).e(ease_curve, 2, rng=(0.5, 0))))
            .align(f.a.r.inset(50), "NW")
            .f(0),
        Glyphwise("OVERLAP TYPE", lambda g:
            Style("ParchVF", 30, DCAY=f.adj(g.i*10).e(ease_curve, 2, rng=(0.5, 1))))
            .align(f.a.r.inset(50), "SE")
            .f(0),
            #ease_curve.copy().scaleToRect(f.a.r.inset(20)).align(f.a.r).fssw(-1, 0, 7)
            ))

@animation((1080, 1080), timeline=360)
def varfont_animation(f):
    ease_curve = P().withRect(1000, lambda r, p: p
        .moveTo(r.psw)
        .ioEaseCurveTo(r.pne, 19, 10))
    
    return (P(
        Glyphwise("DRY\nCLEANERS", lambda g:
            Style("ParchVF", 230, DCAY=f.e(ease_curve, 0, rng=(0.5, 0 if g.l > 0 else 1))))
            .xalign(f.a.r)
            .lead(100)
            .align(f.a.r)
            .align(f.a.r, tx=0)
            .f(0),
            #ease_curve.copy().scaleToRect(f.a.r.inset(20)).align(f.a.r).fssw(-1, 0, 7)
            ))

@b3d_runnable(force_refresh=1)
def setup(blw:BpyWorld):
    (blw
        .delete_previous(materials=False)
        .timeline(Timeline(360, 24), output=setup.output_folder / "p1_"))

    sun = BpyObj.Find("Light")
    (sun.insert_keyframes("rotation_euler",
        (0, lambda bp: bp.rotate(z=-170)),
        (360, lambda bp: bp.rotate(z=-44)))
        #.make_keyframes_linear("rotation_euler")
        )

    (BpyObj.Plane("Projection")
        .scale(3, 3)
        .rotate(x=90)
        .locate(0, 0, 2)
        .material("projection_material", lambda m: m
            .f(0)
            .specular(0)
            .animation(varfont_animation)))