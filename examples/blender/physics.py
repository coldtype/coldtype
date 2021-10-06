from coldtype import *
from coldtype.blender import *

txt = "FALL\nING\nTEXT"

if False: # experimental
    if bpy:
        from coldtype.blender.fluent import BpyWorld, BpyObj

        with BpyWorld().rigidbody(speed=3.5, frame_end=1000):
            (BpyObj.Find("Plane")
                .rigidbody("passive", friction=1, bounce=0))

@b3d_renderable()
def justi(r):
    return (StSt(txt,
        Font.MutatorSans(), 300, wght=0.25)
        .track(100, v=1)
        .map(λ.track_to_rect(r.inset(70)))
        .align(r.inset(50))
        .remove_blanks()
        .pmap(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.275)
                .convert_to_mesh()
                .remesh(5)
                .rigidbody(friction=0.5),
                dn=True,
                zero=True))))
