from coldtype.blender.fluent import BpyObj
from coldtype import *
from coldtype.blender import *
from functools import partial

"""
A two-pass physics animation:

-   when LIVE_PHYSICS is True, a single lockup
    is rendered to blender for a normal physics
    simulation — once you’ve got this looking how
    you want it, you can select all the glyph objects
    and then in the 3d view, select the Object dropdown,
    and then in the Rigid Body menu, select "Bake to Keyframes";
    once that’s complete, you can hide all the glyphs, then come
    back to this file and set LIVE_PHYSICS = False, then resave

-   when LIVE_PHYSICS is False (and the rigid body simulation
    has been baked to keyframes), a variable font animation
    uses the baked keyframes to "fake" the rigid body physics
    simulation (since (as far as I know) it’s impossible to
    do a "true" variable font / callback-based rigid body
    simulation in blender)

"""

LIVE_PHYSICS = True

t = Timeline(65)
r = Rect(1080, 1080)

def build_lockup(wght):
    return (StSt("FALLING", Font.MutatorSans(), 120
        , wdth=1
        , wght=wght)
        .align(r.inset(50))
        .translate(0, 500))

if LIVE_PHYSICS:
    @b3d_runnable()
    def before_bake(bw):
        (bw.deletePrevious()
            .timeline(t, resetFrame=0)
            .renderSettings(128)
            .rigidbody(speed=2, frame_end=1000))
    
    @b3d_renderable(center=(0, 1), upright=1)
    def physics_basis(r):
        letters = (build_lockup(0)
            .pmap(lambda i, p: p
                .tag(f"glyph_{i}")
                .ch(b3d(lambda bp: bp
                    .extrude(0.5)
                    .convertToMesh()
                    .locate_relative(z=i*0.25)
                    .rigidbody(friction=1, bounce=0.95),
                    dn=True,
                    upright=True,
                    zero=True))))
        
        return P(
            letters,
            (P(r.take(200, "S"))
                .tag("surface")
                .ch(b3d(lambda bp: bp
                    .extrude(0.1)
                    .convertToMesh()
                    .rigidbody("passive")
                    , material="surface_material"))
                .ch(b3d_post(lambda bp: bp
                    .rotate(x=88)
                    .locate_relative(z=-2)))))

else:
    @b3d_animation(timeline=t, center=(0, 1), upright=1)
    def physics_upright_curves(f):
        def positioner(i, bp):
            ref = BpyObj.Find(f"glyph_{i}").obj
            bp.locate(ref.location)
            bp.rotate(ref.rotation_euler)
            return bp
        
        return (build_lockup(f.e("eeio", 2))
            .pmap(lambda i, p: p
                .tag(f"curve_{i}")
                .ch(b3d(lambda bp: bp.extrude(0.5),
                    upright=True,
                    zero=True))
                    .ch(b3d_post(partial(positioner, i)))))
