from coldtype.test import *

tl = Timeline(26, fps=23.976, storyboard=[0, 18])

def find_workarea(self):
    return [0, 1, 2]

Timeline.find_workarea = find_workarea

@animation(rect=(1920, 1080), timeline=tl)
def render(f):
    return StyledString(chr(65+f.i), Style(mutator, 1000, wdth=1-f.a.t.progress(f.i).e)).pen().f("hr", 0.5, 0.5).align(f.a.r)