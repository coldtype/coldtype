from coldtype.renderer.state import RendererState
import cv2
from coldtype.test import *
from coldtype.warping import warp_fn
from random import randint
from coldtype.pens.datimage import DATImage
from drafting.text.richtext import RichText
from time import sleep

fnt1 = Font.Cacheable("~/Type/fonts/fonts/_script/BancoPro.otf")
fnt2 = Font.Cacheable("~/Type/fonts/fonts/_script/MistralD.otf")

tl = Timeline(120)

@animation((1080, 1080), rstate=1, timeline=tl)
def stub(f, rs:RendererState):
    if False:
        capture = cv2.VideoCapture(0)
        _, frame = capture.read()
        save_to = "experiments/media/bmpcc/capture{:04d}.jpg".format(f.i-1 if f.i > 0 else tl.duration-1)
        capture.release()

    r = f.a.r

    crv = (DP().define(r=r)
        .gs("$r↙ $r←|cf:=250|$r→|cf|$r↗ ɜ")
        .f(None).s(hsl(0.3)).sw(2))
    
    e = f.a.progress(f.i).e
    amb = crv.ambit()
    ee = crv.take_curve(1).t(e).y/amb.h
    ee = e
    
    #return crv

    txt = (RichText(f.a.r,
        "HELLO\nWorld [v]",
        {"default":Style(fnt1, 100, tu=-50),
        "v":Style(fnt2, 120)})
        .xa()
        .pen()
        .f(0)
        .align(r)
        .cast(DP))
    
    #txt.translate(0, -txt.ambit(tv=1).mxy)
    amb = txt.ambit(tv=1)
    #txt.translate(0, -amb.mxy+(f.a.r.h+amb.h)*ee)
    
    #rs.notify_external(f.i)
    
    return DPS([
        DP(r).f(0),
        txt.flatten(3).nlt(warp_fn(f.i*5, f.i*5)).f(1),
        #crv
    ])