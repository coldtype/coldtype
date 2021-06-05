from coldtype.test import *
from string import ascii_uppercase

fnt = Font.Cacheable("~/Type/fonts/fonts/Forwardv0-2-Light.otf")

@animation((1920, 1080), timeline=len(ascii_uppercase), bg=0, cv2caps=[0])
def to_be_captured(f):
    return DPS([
        DP(f.a.r).f(0),
        (StSt(ascii_uppercase[f.i], fnt, 500)
            .align(f.a.r)
            .translate(130, -100)
            .scale(0.8)
            .f(1))])
