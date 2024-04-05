from coldtype import *

@renderable((1080, 540), bg=1)
def aligns(r):
    ri = r.inset(100)
    return (P(
        P(r.inset(50)).fssw(-1, 0, 1),
        StSt("Coldest\nType".upper(), Font.MuSan(), fs:=72).xalign(ri, "W").align(ri, "NW"),
        StSt("Coldest\nType".upper(), Font.MuSan(), fs).xalign(ri).align(ri),
        StSt("Coldest\nType".upper(), Font.MuSan(), fs).xalign(ri, "E").align(ri, "SE"),
        ))
