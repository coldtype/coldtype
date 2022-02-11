from coldtype import *
from coldtype.blender import *

"""
A 3D Physics simulation that uses two animations:

-   the first uses lo-res polygons to do the actual physics

-   the second uses bezier curves parented to the lo-res polygons,
    which means in the end result you see the hi-res shapes
    behaving in the manner of the lo-res polygons

(both animations are based on a single "lockup")
"""

txt = "FALL\nING\nTEXT"

@b3d_runnable()
def setup(bw:BpyWorld):
    with (bw.deselect_all()
        .delete_previous()
        .timeline(Timeline(250))
        .render_settings(128)
        .rigidbody(speed=1.5, frame_end=1000)):
            (BpyObj.Find("Plane")
                .rigidbody("passive", friction=1, bounce=0))

r = Rect(1080, 1080)
lockup = (StSt(txt, Font.Find("PlincBubbleGum33.otf"), 400)
    .track(100, v=1)
    .map(lambda p: p.track_to_rect(r.inset(70)))
    .align(r.inset(50))
    .deblank()
    .collapse())

@b3d_renderable(center=(0, 1), upright=1)
def physics_upright(r):
    return (lockup.copy()
        .pmap(lambda i, p: p
            .tag(f"glyph_{i}")
            .ch(b3d(lambda bp: bp
                .extrude(0.5)
                .convert_to_mesh()
                .remesh(3)
                .apply_modifier("Remesh")
                .rigidbody(friction=1, bounce=0),
                dn=True,
                upright=True,
                zero=True))
            .ch(b3d_post(lambda bp: bp
                .locate_relative(0, i*0.1)))))

@b3d_renderable(center=(0, 1), upright=1)
def physics_upright_curves(r):
    return (lockup.copy()
        .pmap(lambda i, p: p
            .tag(f"curve_{i}")
            .ch(b3d(lambda bp: bp
                .extrude(0.5),
                dn=True,
                upright=True,
                zero=True))
            .ch(b3d_post(lambda bp: bp
                .locate_relative(0, i*0.1)
                .parent(f"glyph_{i}", hide=True)))))
