from coldtype.animation import *

def render(f):
    return StyledString("e", Style("≈/Obviously", 500, fill=1, wdth=1, wght=1)).pen().align(f.a.r)

animation = Animation(render)