from coldtype import *
from coldtype.blender import *

"""
An arch, dynamically generated from a bezier curve;
then physics are enabled and the whole thing falls down
"""

tl = Timeline(90, fps=30)

@b3d_runnable()
def setup(bpw:BpyWorld):
    BpyObj.Find("Cube").delete()
    BpyObj.Find("Light").locate(y=-5)

    (bpw.delete_previous(materials=False)
        .cycles(32, False, Rect(1080, 1080))
        .timeline(tl, output=setup.output_folder / "arch1_")
        .rigidbody(2.5, 300))
 
    (BpyObj.Cube("Floor")
        .scale(x=100, y=100, z=0.2)
        .locate(z=1.65)
        .apply_scale()
        .rigidbody("passive", friction=1, bounce=0)
        .material("floor-material", lambda m: m
            .f(bw(0))))

@b3d_renderable(reset_to_zero=1, upright=1, center=(0, 1))
def arch(r):
    r = r.inset(200)
    curve:P = (P()
        .moveTo(r.psw)
        .boxCurveTo(r.pn, "NW", factor:=.65)
        .boxCurveTo(r.pse, "NE", factor)
        .fssw(-1, 0, 2))

    return (P().enumerate(curve.samples(60), lambda x: P()
        .declare(
            q:=0.49,
            start:=x.el.pt.project(x.el.tan, d:=100),
            end:=x.el.pt.project(x.el.tan, -d))
        .moveTo(start.interp(q, x.el.next.pt.project(x.el.next.tan, d)))
        .lineTo(start.interp(q, x.el.prev.pt.project(x.el.prev.tan, d)))
        .lineTo(end.interp(q, x.el.prev.pt.project(x.el.prev.tan, -d)))
        .lineTo(end.interp(q, x.el.next.pt.project(x.el.next.tan, -d)))
        .closePath()
        .f(0)
        .tag(f"sample_{x.i}")
        .ch(b3d(lambda bp: bp
            .extrude(1.0)
            .convert_to_mesh()
            .rigidbody(friction=1, bounce=0)
            , upright=1
            , zero=1))))