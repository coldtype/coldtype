from coldtype import *
from coldtype.blender import *

samples, x, y, z, frames = [
    (1.5, 3, 0.5, 5, 120),
    (0.5, 3, 0.25, 5, 120),
    (0.25, 3, 0.15, 3, 120),
    (1.2, 3, 0.25, 10, 120)
][2]

letter = "A"
suffix = f"alphabet_capZ_{samples}_{x}_{y}_{z}__"

rs1 = random_series(seed=2)

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

    curve = P().oval(Rect(10)).centerZero().repeat(1).subsegment(0, 0.505)
    
    points = curve.samples(samples)
    dominos = []

    for idx, pt in enumerate(points[:-2]):
        if rs1[idx] <= 1: #> 0.85:
            dominos.append(
                #BpyObj.Cube(f"Cube_{pt.idx}")
                #.dimensions(x, y, z)
                BpyObj.Curve(f"Cube_{pt.idx}")
                .draw(StSt("NICE", "AdGothic", 4, wdth=1).pen())
                .rotate(x=90)
                .extrude(0.05)
                .convert_to_mesh()
                .locate(z=z/2)
                .rotate(z=pt.tan)
                .locate(x=pt.pt[0], y=pt.pt[1])
                .material("letter_mat"))

    pt = points[0]
    a = pt.pt.project(pt.tan, -2).project(pt.tan-90, -0.5)
    b = pt.pt.project(pt.tan, -2).project(pt.tan-90, 0.5)
    c = pt.pt.project(pt.tan, -10)

    (BpyObj.Cube("Catalyst")
        .dimensions(2, 0.65, zz:=1.75)
        .locate(x=-1, y=0, z=zz)
        .origin_to_cursor()
        .rotate(z=pt.tan+180)
        .apply_transform()
        .rigidbody("passive", animated=True, friction=1)
        .hide()
        .insert_keyframes("location",
            (0, lambda bp: bp.locate(x=a.x, y=a.y, z=zz/2)),
            (20, lambda bp: bp.locate(x=b.x, y=b.y, z=zz/2)),
            (50, lambda bp: bp.locate(x=c.x, y=c.y, z=zz/2))))

    for dm in dominos:
        (dm.apply_transform()
            .origin_to_geometry()
            .rigidbody(mass=10, friction=0.35, deactivated=True))