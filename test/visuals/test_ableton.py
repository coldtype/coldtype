from coldtype import *
from coldtype.time.nle.ableton import AbletonReader, AbletonMIDITrack, save_test_xml, AbletonAudioTrack
from coldtype.warping import warp_fn
from random import randint

from pprint import pprint

ar = AbletonReader("~/Audio/loopprojs/test_read Project/test_read2.als")
save_test_xml(ar.lx)

drums:AbletonMIDITrack = ar.tracks[0]
guitar:AbletonAudioTrack = ar.tracks[1]
synth:AbletonMIDITrack = ar.tracks[2]
synth_min, synth_max = synth.range()

o = Font("~/Type/fonts/fonts/ObviouslyVariable.ttf")

@animation(Rect(1080, 1080), timeline=ar, storyboard=[29], bg=0)
def ableton(f):
    b, t = f.a.r.divide(300, "mny")

    def dp(s, notes, reverb, h, stroke=False):
        n = drums.fv(f.i, lambda t: t.name in notes, reverb)
        e = n.ease()
        color = hsl(h+0.1*e, s=0.6, l=0.6, a=e*0.95)
        #color = hsl(0, 0, 1, a=e*0.95)
        style = Style(o, 350+10*e, wdth=0.1+e*0.1, wght=0.75+e*0.25, slnt=e*0.25, ro=1, tu=-30)
        _dp = StyledString(s, style).fit(f.a.r.w-100).pen().removeOverlap().align(t).translate(0, -50)
        if stroke:
            _dp.f(None).s(color).sw(10)
        else:
            _dp.f(color)
        return _dp
    
    warp = warp_fn(xa=10, ya=10, mult=95, base=0)
    warp2 = warp_fn(xa=10, ya=10, mult=35, base=0)

    sns = synth.fv(f.i, reverb=[2, 30], accumulate=1)
    sdp = StyledString("BCDE", Style(o, 250, wdth=0.5, wght=1, tu=-50, r=1, ro=1)).pens().align(b).translate(0, 50).f(None)

    for s in sns:
        n = 3-[59, 60, 62, 64].index(int(s.timeable.name))
        sdp[n].rotate(-45*s.ease()).f(hsl(s.ease(), l=0.7, a=s.ease()))
    
    sdp.pmap(lambda i,p: p.flatten(5).nonlinear_transform(warp2))
    
    return DATPens([
        dp("KICK", ["36"], [5, 25], 0.9),
        dp("RIMSHOT", ["39"], [3, 20], 0.0),
        dp("SNARE", ["40", "41"], [5, 20], 0.6),
        dp("CLAP", ["42"], [5, 50], 0.65),
        dp("HAT", ["43"], [2, 10], 0.15, True),
        dp("HAT", ["44"], [3, 50], 0.15, True),
        dp("CLAVE", ["46"], [5, 100], 0.4).flatten(10).nonlinear_transform(warp),
        dp("COWBELL", ["47"], [5, 20], 0.7).rotate(15),
        dp("TOMTOM", ["48", "49", "50"], [3, 25], 0.1),
        sdp
    ])