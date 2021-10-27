from coldtype.blender.fluent import BpyObj
from coldtype import *
from coldtype.blender import *
from functools import partial

PREBAKE = False

t = Timeline(42)
r = Rect(1080, 1080)

def build_lockup(wght):
    return (StSt("Impact", Font.Find("Humanist"), 200
        , opsz=1
        , wght=wght)
        .align(r.inset(50))
        .translate(0, 500))

if PREBAKE:
    @b3d_runnable()
    def before_bake(bw):
        with (bw
            .delete_previous()
            .timeline(t)
            .render_settings(128)
            .rigidbody(speed=3, frame_end=1000)):
                (BpyObj.Find("Plane")
                    .rigidbody("passive"))
    
    @b3d_renderable(center=(0, 1), upright=1)
    def physics_basis(r):
        return (build_lockup(1)
            .pmap(lambda i, p: p
                .tag(f"glyph_{i}")
                .ch(b3d(lambda bp: bp
                    .extrude(0.5)
                    .convert_to_mesh()
                    .rigidbody(friction=1, bounce=0.95),
                    dn=True,
                    upright=True,
                    zero=True))))

else:
    @b3d_animation(timeline=t, center=(0, 1), upright=1)
    def physics_upright_curves(f):
        def positioner(i, bp):
            ref = BpyObj.Find(f"glyph_{i}").obj
            bp.locate(ref.location)
            bp.rotate(ref.rotation_euler)
            return bp
        
        return (build_lockup(f.e("eeio", 4))
            .pmap(lambda i, p: p
                .tag(f"curve_{i}")
                .ch(b3d(lambda bp: bp.extrude(0.5),
                    upright=True,
                    zero=True))
                    .ch(b3d_post(partial(positioner, i)))))
