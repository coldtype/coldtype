from coldtype import *
from coldtype.animation import *

font = Font("ç/MutatorSans.ttf")

@animation(rect=(1920, 1080), storyboard=[0,25], duration=26)
def render(f):
    return StyledString(chr(65+f.i), Style(font, 1000, wdth=f.a.progress(f.i).e)).pen().f("hr", 0.5, 0.5).align(f.a.r)