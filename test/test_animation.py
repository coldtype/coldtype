from coldtype import *
from coldtype.animation import *

font = Font("≈/LautsprecherDJR-Regular.otf")

@animation(rect=(1920, 1080), storyboard=[0,3])
def render(f):
    return StyledString(str(f.i), Style(font, 1000)).pen().f("random").align(f.a.r)