from coldtype import *
from coldtype.blender import *

samples, x, y, z, frames = [
    (1.5, 3, 0.5, 5, 120),
    (0.5, 3, 0.25, 5, 120),
    (0.25, 3, 0.15, 5, 180),
    (1.2, 3, 0.25, 5, 90)
][3]

letter = "A"
suffix = f"alphabet_{samples}_{x}_{y}_{z}__"

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def setup(bpw:BpyWorld):
    (bpw.delete_previous(materials=False)
        .timeline(Timeline(frames, 30), resetFrame=0
            , output=setup.output_folder / suffix)
        .rigidbody(2.5, 250))
    
    (BpyObj.Cube("Floor")
        .dimensions(x=30, y=30, z=1)
        .locate(z=-0.5)
        .rigidbody("passive")
        .material("floor_mat"))

    r = Rect(10)
    curve = P().oval(Rect(10)).centerZero().repeat(1).subsegment(0, 0.505)
    curve = P().line([r.pw, r.pe]).endPath().centerZero().t(0, -1)
    
    points = curve.samples(samples)
    dominos = []

    text = "MONUMENTAL"

    for pt in points:
        if False:
            dominos.append(BpyObj.Cube(f"Cube_{pt.idx}")
                .dimensions(x, y, z)
                .locate(z=z/2)
                .rotate(z=pt.tan)
                .locate(x=pt.pt[0], y=pt.pt[1])
                .material("letter_mat"))
        else:
            try:
                glyph = StSt(text[pt.idx], Font.MuSan(), 5, wdth=1, wght=0.25, opsz=1).pen()
                glyph.t(-glyph.ambit(tx=1).x, -glyph.ambit(ty=1).y)
            except IndexError:
                glyph = None

            if glyph:
                dominos.append(BpyObj.Curve(f"Letter_{pt.idx}")
                    .draw(glyph)
                    .extrude(0.35)
                    .with_temp_origin((0,0,0), lambda bp: bp.rotate(y=-90))
                    .convert_to_mesh()
                    .apply_transform()
                    #.rotate(z=pt.tan+180)
                    #.rotate(z=pt.tan+180)
                    .locate(x=pt.pt[0], y=pt.pt[1])
                    #.convert_to_mesh()
                    #.apply_transform()
                    .material("letter_mat")
                    )

    pt = points[0]
    a = pt.pt.project(pt.tan, 0).project(pt.tan-90, -0.5)
    b = pt.pt.project(pt.tan, 0).project(pt.tan-90, 1.5)

    (BpyObj.Cube("Catalyst")
        .dimensions(xx:=2, 0.65, zz:=1.75)
        .locate(x=-1, y=0, z=zz)
        .origin_to_cursor()
        .rotate(z=pt.tan+180)
        .apply_transform()
        .rigidbody("passive", animated=True, friction=1)
        #.hide()
        .insert_keyframes("location",
            (0, lambda bp: bp.locate(x=a.x, y=a.y, z=zz/2)),
            (20, lambda bp: bp.locate(x=b.x, y=b.y, z=zz/2)),
            (50, lambda bp: bp.locate(x=a.x, y=a.y, z=zz/2)))
        #.origin_to_geometry()
        )

    for dm in dominos:
        (dm.apply_transform()
            .origin_to_geometry()
            .rigidbody(mass=10, friction=0.35, deactivated=True))