from coldtype.blender import *

BPH.Clear()

r = Rect(0, 0, 1000, 1000)
tc = BPH.Collection("Text")
fnt = Font.Cacheable("~/Type/fonts/fonts/CheeeVariable.ttf")

(DATPen(r)
    .f(hsl(0.9))
    .tag("Frame")
    .cast(BlenderPen)
    .draw(tc, plane=1))

@b3d_animation(30)
def draw_txt(f):
    (StSt("YO!", fnt, 500, yest=f.ie("qeio", 2), grvt=f.e(1))
        .pen()
        .align(r)
        .tag("HEY")
        .cast(BlenderPen)
        .draw(tc))