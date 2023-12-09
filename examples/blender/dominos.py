from coldtype import *
from coldtype.blender import *

frames = 160
suffix = "falling_"
text = """FALLING
DOWN"""

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def setup(bpw:BpyWorld):
    (bpw.delete_previous(materials=False)
        .timeline(Timeline(frames, 30), resetFrame=0
            , output=setup.output_folder / suffix)
        .rigidbody(2.5, frames))
    
    (BpyObj.Cube("Floor")
        .dimensions(x=30, y=30, z=1)
        .locate(z=-0.5)
        .rigidbody("passive")
        .material("floor_mat"))

    r = Rect(10)
    
    curves = P(
        P().line([r.pw, r.pe]).endPath().centerZero().t(0, 0),
        P().line([r.pw, r.pe]).endPath().centerZero().t(0, -4),
        #P().line([r.pw, r.pe]).endPath().centerZero().t(0, -4*2),
    ).t(-1.5, 2.5)

    dominos = []
    
    for idx, curve in enumerate(curves):
        points = curve.samples(1.3)
        txt = text.split("\n")[idx]

        for pt in points:
            try:
                glyph = StSt(txt[pt.idx], Font.MuSan(), 4, wdth=1, wght=0).pen()
                glyph.t(-glyph.ambit(tx=1).x, -glyph.ambit(ty=1).y)
            except IndexError:
                glyph = None

            if glyph:
                dominos.append(BpyObj.Curve(f"Letter_{pt.idx}")
                    .draw(glyph)
                    .extrude(0.15)
                    .with_temp_origin((0,0,0), lambda bp: bp.rotate(y=-90))
                    .convert_to_mesh()
                    .apply_transform()
                    .locate(x=pt.pt[0], y=pt.pt[1])
                    .material("letter_mat"))

        pt = points[0]
        a = pt.pt.o(0, 1.25).project(pt.tan-90, -0.5)
        b = pt.pt.o(0, 1.25).project(pt.tan-90, 0.5)
        c = a.project(pt.tan-90, -3)

        czh = 3
        (BpyObj.Cube("Catalyst")
            .dimensions(0.25, 2, cz:=0.5)
            .locate(x=a.x, y=a.y, z=czh)
            # .origin_to_cursor()
            # .rotate(z=pt.tan+180)
            # .apply_transform()
            .rigidbody("passive", animated=True, friction=1)
            .hide()
            .insert_keyframes("location",
                (0+idx*(n:=50), lambda bp: bp.locate(x=a.x, y=a.y, z=czh)),
                (10+idx*n, lambda bp: bp.locate(x=b.x, y=b.y, z=czh)),
                (20+idx*n, lambda bp: bp.locate(x=c.x, y=c.y, z=czh)))
            # #.origin_to_geometry()
            .set_frame(0)
            )

    dm:BpyObj
    for dm in dominos:
        (dm.apply_transform()
            .origin_to_geometry()
            .rigidbody(mass=10, friction=0.35, deactivated=True))