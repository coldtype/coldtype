from coldtype import *
from coldtype.blender import *

"""
Demonstration of how to display a dynamic
image on a plane
"""

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

@renderable((1080, 1080), bg=0, render_bg=0)
def embedded_image(r):
    char = "A"
    if bpy:
        char = chars[bpy.context.scene.frame_current]
    
    return (StSt(char, Font.MutatorSans(), 1000, ro=1, wdth=0, wght=1)
        .align(r)
        .pen()
        .f(1))

@b3d_runnable()
def setup(bpw:BpyWorld):
    (bpw.delete_previous()
        .cycles(128))

@b3d_animation(tl=len(chars), force_refresh=True)
def anim1(f):
    proj = BpyObj.Find("Reprojection")
    if not proj.obj:
        proj = BpyObj.Plane("Reprojection").scale(2.5, 2.5)
    
    (proj.material("embedded_image", lambda m: m
            .image(embedded_image, emission=0, render=True))
        .rotate(x=-55))