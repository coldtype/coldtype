from coldtype import *
from coldtype.blender import *

"""
A classic 5-by-5 Noordzij Cube, displaying any
variable font with three axes

(https://letterror.com/articles/noordzij-cube.html)
"""

fnt = Font.Find("ObviouslyV")

d = 5

@b3d_runnable()
def setup(bpw:BpyWorld):
    (bpw.delete_previous()
        .cycles(128)
        .timeline(Timeline(240)
            , resetFrame=0
            , output=setup.output_folder / "noord1_"))
    
    (BpyObj.Cube("Floor")
        .dimensions(x=d*2, y=d*2, z=0.25)
        .locate(x=d, y=d)
        .origin_to_cursor()
        .locate(x=-d/2, y=-d/2, z=-1)
        .material("floor_mat", lambda m: m
            .f(0)
            .specular(0)
            .roughness(1)))
    
    pivot = (BpyObj.Empty("Center")
        .locate(x=(d-1)/2, y=(d-1)/2, z=0)
        .insert_keyframes("rotation_euler",
            (0, lambda bp: bp.rotate()),
            (240, lambda bp: bp.rotate(z=360)))
        .make_keyframes_linear("rotation_euler"))
    
    (BpyObj.Find("Camera").parent(pivot))
    
    def add_glyph(x, y, z):
        (BpyObj.Curve(f"Glyph_{x}_{y}_{z}")
            .draw(StSt("A", fnt, 0.5
                , slnt=x/(d-1)
                , wdth=(y/(d-1))
                , wght=1-((z/(d-1))))
                .centerZero()
                .pen())
            .rotate(x=90)
            .locate(x=x, y=y, z=z)
            .extrude(0.1)
            .convert_to_mesh()
            .material(f"letter_mat_{y}", lambda m: m
                .f(1)
                #.f(hsl(y/(d+1), 1, 0.8))
                .specular(0)
                .roughness(1)))
    
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
                add_glyph(x, y, z)