from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer
from coldtype.fx.skia import phototype

obv = Font.Find("ObviouslyV", "__variables")

bt = BlenderTimeline(ººBLENDERºº, 5400)

ifg = bt.interpretWords(include="+1")
action = bt.interpretWords(include="+2")
adlib = bt.interpretWords(include="+4")
suggestion = bt.interpretWords(include="+5")

@b3d_sequencer((1920, 1080)
, timeline=bt
, bg=None
, render_bg=False
, live_preview=0
, live_preview_scale=0.25
)
def lyrics(f:Frame):
    r_ifg = f.a.r.inset(650, 446)

    def obvi(c):
        txt = c.text
        return (txt.upper(), Style(obv, 120, wdth=0.5, wght=0.85, ss01=1, slnt=1, tu=-20))

    top = (ifg.currentGroup(f.i)
        .pens(f.i, obvi, fit=r_ifg.w)
        .align(r_ifg, "N")
        .removeFutures()
        .fssw(1, 0, 10, 1))

    bottom = (action.currentGroup(f.i)
        .pens(f.i, obvi, fit=r_ifg.w)
        .align(r_ifg, "S")
        .removeFutures()
        .fssw(1, 0, 10, 1))
    
    try:
        if "a song" in bottom[0][0][0].data("clip").text:
            bottom[0][0][0].filter(lambda idx, p: idx > 3)
        if "a bike" in bottom[0][0][0].data("clip").text:
            bottom[0][0][0].filter(lambda idx, p: idx > 3)
        if "a juice" in bottom[0][0][0].data("clip").text:
            bottom[0][0][0].filter(lambda idx, p: idx > 4)
        if "a cat" in bottom[0][0][0].data("clip").text:
            bottom[0][0][0].filter(lambda idx, p: idx > 2)
    except Exception as _:
        pass
    
    lockup = P(top, bottom)#.t(0, -220)

    ad = (adlib.currentGroup(f.i)
        .pens(f.i, lambda x: (x.text, Style("Lovesong", 100)))
        #.scale(0.5, 1)
        .align(f.a.r.drop(600, "S"), "CX")
        .rotate(15)
        .removeFutures()
        .pen()
        .fssw(1, 0, 10, 1))
    
    sugg = (suggestion.currentGroup(f.i)
        .pens(f.i, lambda x: (x.text, Style("Softie", 200, wght=0.25)))
        #.scale(0.5, 1)
        .align(f.a.r.inset(250).drop(340, "S"), "N")
        .rotate(-15)
        .removeFutures()
        .pen()
        .fssw(1, 0, 10, 1))

    style = bt.current(3)
    if style.name:
        if style.name == "scramble":
            lockup[0].mapv(lambda p: p.rotate(35))
            lockup[1].mapv(lambda p: p.rotate(-15))
        elif style.name == "scramble3":
            lockup[0].mapv(lambda p: p.rotate(-15))
            lockup[1].mapv(lambda p: p.rotate(35))
        elif style.name == "scramble2":
            lockup[0].mapv(lambda p: p.rotate(-15))
            lockup[1].mapv(lambda p: p.rotate(35))
            lockup.rotate(-15)
            ad.rotate(-20)
        
        if style.name == "fade":
            o = style.e("l", 0, rng=(1, 0))
            lockup.alpha(o)
            ad.alpha(o)

    return P(P(lockup + ad).t(0, -220) + sugg).ch(phototype(f.a.r, 2, 150, 30))