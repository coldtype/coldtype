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
        .rigidbody(0.5, 250)
        .timeline(Timeline(120), resetFrame=0))
    
    (BpyObj.Cube("Floor")
        .dimensions(x=d*2, y=d*2, z=0.25)
        .locate(x=d, y=d)
        .origin_to_cursor()
        .locate(x=-d/2, y=-d/2, z=-1)
        .rigidbody("passive")
        .material("floor_mat", lambda m: m
            .f(0)
            .specular(0)
            .roughness(1)))
    
    for z in range(0, d):
        for y in range(0, d):
            for x in range(0, d):
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
                    .rigidbody()
                    .material(f"letter_mat_{y}", lambda m: m
                        .f(1)
                        #.f(hsl(y/(d+1), 1, 0.8))
                        .specular(0)
                        .roughness(1)))
    
    (BpyObj.Find("Camera")
        .constrain_child_of(BpyObj.Find("Glyph_4_4_4")
            , influence=0.5))