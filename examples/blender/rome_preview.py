from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer
from coldtype.raster import *
from noise import pnoise1

fnt = Font.Find("NCND", "__variables")
#fnt = Font.Find("MDPrimer-Bold")
fnt = Font.Find("PolymathV")

rs1 = random_series(0.35, 0.75)

img = SkiaImage(f"~/Downloads/theokeyboard.png")

@animation(img.rect()
, timeline=Timeline(30)
, bg=hsl(0.3)
, render_bg=False
)
def lyrics(f:Frame):
    r = f.a.r.take(170, "S")
    yellow = hsl(0.14, 1, 0.65)
    yellow = bw(1)
    #yellow = bw(0)
    
    slug = (StSt("Rome Wasn’t Built\nin a Day".upper(), fnt, 302, wght=0.85, space=1400, leading=160)
        .xalign(r)
        #.wordPens()
        #.map(lambda i, p: p.t(0, -i*110))
        .align(f.a.r.take(1, "S"))
        .t(0, 110)
        .ch(filmjitter(f.e("l", 20), scale=(1.5, 3)))
        .f(1)
        .ch(phototype(f.a.r, 1.5, 140, 83, fill=yellow)))

    analog_slug = (
        slug
        .up()
        .append(P().rect(f.a.r)
           .f(-1)
           .ch(spackle(cut=15, cutw=1, base=f.i, fill=bw(1)))
           .blendmode(BlendMode.Cycle(35)))
        .ch(precompose(f.a.r))
        .ch(blur(3.5))
        .ch(precompose(f.a.r)))
    

    return (P(
        img.copy(),
        # (P(analog_slug.copy(),
        #     img.ch(phototype(f.a.r, 3, 113, 0)).blendmode(BlendMode.Cycle(9)))
        #     .ch(precompose(f.a.r))),
        (P(analog_slug.copy().t(0, 0).ch(fill(bw(0))),
            img.ch(phototype(f.a.r, 60, 100, 11)).blendmode(BlendMode.Cycle(38))
            )
            .ch(precompose(f.a.r))
            .ch(invert())
            .ch(precompose(f.a.r))
            .ch(blur(1.25)))
            .ch(precompose(f.a.r))
            #.ch(temptone(0.67, 0.36))
            #.ch(precompose(f.a.r))
            #.ch(expose(1.95+pnoise1(f.e("l", 5))*10))
            ,
    ))