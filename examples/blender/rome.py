from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer
from coldtype.raster import *
from noise import pnoise1

fnt = Font.Find("NCND", "__variables")
#fnt = Font.Find("MDPrimer-Bold")
fnt = Font.Find("PolymathV")

bt = BlenderTimeline(ººBLENDERºº, 5400, fps=24)

words = bt.interpretWords(include="+3")
action = bt.interpretWords(include="+4")
styling = bt.interpretWords(include="+5")
#adlib = bt.interpretWords(include="+4")
#suggestion = bt.interpretWords(include="+5")

rs1 = random_series(0.35, 0.75)

@b3d_sequencer((1920, 1080)
, timeline=bt
, bg=hsl(0.3)
, render_bg=False
, live_preview_scale=0.35
)
def lyrics(f:Frame):
    #return None

    try:
        word_by_word = action.current(f.i).text.strip() == "words"
    except:
        word_by_word = False
    
    try:
        titles = styling.current(f.i).text.strip() == "titles"
    except:
        titles = False

    r = f.a.r.take(170, "S")
    yellow = hsl(0.14, 1, 0.65)
    yellow = bw(1)
    #yellow = bw(0)

    def ncnd(c):
        txt = c.text
        if txt.endswith("plus"):
            txt = " +"
        wght = rs1[c.clip.idx]
        wght = 0.85
        if titles:
            return (txt.upper(), Style(fnt, 32 if "Theo" in txt else 52, wght=0.85, space=2000 if "Rome" in txt else 600))
        return (txt.lower(), Style(fnt, 52, wght=wght, space=600))
    
    slug = (words.currentGroup(f.i)
        .pens(f.i, ncnd)
        .xalign(r)
        .cond(titles, lambda p: p.align(f.a.r.take(1, "S")), lambda p: p.align(r, "N"))
        #.align(r, "N")
        .cond(word_by_word, lambda p: p.removeFutures())
        #.removeFutures()
        #.fssw(1, 0, 10, 1)
        .ch(filmjitter(f.e("l", 20), scale=(1.5, 3)))
        .f(1)
        .layer(
            #lambda p: p.fssw(1, 1, 1).ch(phototype(f.a.r, 2, 130, 70, fill=0)).t(o:=1.75, -o).ch(precompose(f.a.r)).ch(fill(bw(0, 0.85))),
            lambda p: p.ch(phototype(f.a.r, 1.5, 140, 83, fill=yellow))
            )
        #.pen()
        #.xor(lambda p: P(p.ambit(tx=1, ty=1).inset(-4, 0)))
        )
    
    img = SkiaImage(f"~/Video/Theo/rome/v2images/romeimages{(86400 + f.i):08d}.png")

    analog_slug = (
        slug
        .up()
        .append(P().rect(f.a.r)
           .f(-1)
           .ch(spackle(cut=5, cutw=1, base=f.i, fill=bw(1)))
           .blendmode(BlendMode.Cycle(35)))
        .ch(precompose(f.a.r))
        .ch(blur(0.5))
        .ch(precompose(f.a.r)))
    

    return (P(
        img.copy(),
        # (P(analog_slug.copy(),
        #     img.ch(phototype(f.a.r, 3, 113, 0)).blendmode(BlendMode.Cycle(9)))
        #     .ch(precompose(f.a.r))),
        (P(analog_slug.copy().t(0, 0).ch(fill(bw(0))),
            img.ch(phototype(f.a.r, 10, 70, 11)).blendmode(BlendMode.Cycle(38))
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