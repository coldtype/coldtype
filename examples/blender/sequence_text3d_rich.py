from coldtype import *
from coldtype.blender import *

bt = BlenderTimeline(ººBLENDERºº, 120)
channel1 = bt.interpretWords(include="+1 +2")

@b3d_runnable(playback=B3DPlayback.AlwaysStop)
def prerun(bw):
    bw.delete_previous(materials=False)

@b3d_animation((1080, 1080), timeline=bt)
def sequence(f:Frame):
    try: BpyWorld().delete_previous(materials=False)
    except: pass

    default_style = Style(Font.JetBrainsMono(), 100, wght=1)

    def setter(c):
        style = default_style
        if "script" in c.styles:
            style = Style(Font.RecMono(), 100, wght=1)
        return [c.text.lower(), style]
    
    return (P(
        channel1
            .currentGroup(f.i)
            .pens(f.i, setter)
            .align(f.a.r)
            .removeFutures()
            .mapv(lambda p: p
                .declare(font:=str(p.parent().data("style", default_style).font.path))
                .ch(b3d(lambda bp: bp
                    .extrude(1.5)
                    .material("mat1" if "JetBrains" in font else "mat2")
                    )))
        ,
        StSt(str(f.i), Font.JBMono(), 72, wght=f.e("eeio"))
            .align(f.a.r.take(200, "S"), tx=0)
            .f(1)
            .pen()
            .ch(b3d(lambda bp: bp
                .extrude(f.e("l", 0, rng=(0.1, 1)))
                .material("mat3")))))