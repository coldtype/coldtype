from coldtype import *

font = Font("ç/MutatorSans.ttf")
tl = Timeline(26, fps=23.976, storyboard=[0, 18])

@animation(rect=(1920, 1080), timeline=tl)
def render(f):
    return StyledString(chr(65+f.i), Style(font, 1000, wdth=1-f.a.t.progress(f.i).e)).pen().f("hr", 0.5, 0.5).align(f.a.r)