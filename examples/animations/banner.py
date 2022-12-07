from coldtype import *
from coldtype.fx.skia import phototype

kfs = [
    dict(wdth=0, rotate=0, tu=300),
    dict(wdth=1, rotate=15, tu=-150),
    dict(wdth=0.25, rotate=-15, tu=350),
    dict(wdth=0.75, rotate=0, tu=-175),
    dict(wdth=0.5, rotate=25, tu=100),
]

# Demonstrating slight ambiguity
# in single-frame vs. block syntax
# i.e. equivalent when multiplier=1
# but different at multiplier>1

at = AsciiTimeline(3, 30, """
                                        <
[0   ]  [1   ]  [2   ]  [3   ]  [4   ]   
A    A  B    B  C    C  D    D  E    E
""", {
    "0": kfs[0], "1": kfs[1], "2": kfs[2],
    "3": kfs[3], "4": kfs[4],
    "A": kfs[0], "B": kfs[1], "C": kfs[2],
    "D": kfs[3], "E": kfs[4],
})

@animation(timeline=at, bg=1, rect=(1500, 300*2))
def render(f):
    return P(
        StSt("COLDTYPE", Font.ColdObvi(), 250
            , **at.kf("eeo", lines=(1,))
            , r=1 , ro=1)
            .align(f.a.r.take(0.5, "N"), tx=0)
            .fssw(1, 0, 20)
            .sf(1)
            .ch(phototype(f.a.r, 1.5, 200, 30, 0)),
        StSt("COLDTYPE", Font.ColdObvi(), 250
            , **at.kf("eeo", lines=(2,))
            , r=1 , ro=1)
            .align(f.a.r.take(0.5, "S"), tx=0)
            .fssw(1, 0, 20)
            .sf(1)
            .ch(phototype(f.a.r, 1.5, 200, 30, 0)))