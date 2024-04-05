from coldtype import *
from coldtype.blender import *

txt = "LETTERS\nCOLORFUL\nA LOT OF\nCOME\nHERE"

@b3d_runnable()
def setup(bw:BpyWorld):
    (bw.delete_previous()
        .timeline(Timeline(150), resetFrame=0)
        .rigidbody(speed=0.5, frame_end=1000))

#@b3d_renderable(center=(0, 1), upright=1)
def justi(r):
    #return None
    letters = (StSt(txt, "Streco", 150)
        .xalign(r)
        .track(1000, v=1)
        .align(r.inset(50), y="S")
        .t(0, 1080)
        .deblank()
        .collapse()
        .map(lambda p: p.explode())
        .collapse()
        .mapv(lambda i, p: p
            .tag(f"glyph_{i}")
            .f(hsl(random()))
            .ch(b3d(lambda bp: bp
                .extrude(0.35)
                .convertToMesh()
                .rigidbody(friction=0.2, bounce=0.2)
                .specular(0)
                .roughness(1)
                , dn=True
                , upright=1
                , zero=True
                , material="auto"))))
    
    def wall(tag, _r, depth=0.5, yShift=0):
        return (P(_r).tag(tag)
            .ch(b3d(lambda bp: bp
                .extrude(depth)
                .convertToMesh()
                .rigidbody("passive")
                , material="wall_material"))
            .ch(b3d_post(lambda bp: bp
                .locate_relative(y=yShift)
                .hide()
                )))
    
    return (P(
        letters,
        # (P(
        #     wall("_front_wall", r, 0.01, 0.4),
        #     wall("_back_wall", r, 0.01, -0.4),
        #     wall("_floor", r.take(50, "S")),
        #     wall("_west_wall", r.take(50, "W")),
        #     wall("_east_wall", r.take(50, "E"))))
            ))
