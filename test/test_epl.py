from coldtype import *
import re

# rg = re.compile("["+"".join(EPL_SYMBOLS.keys())+"]{2,}")
# s = "$ri↑↗↖"
# mm = re.findall(rg, s)
# if mm:
#     first = mm[0][0]
#     a, b = s.split(first)
#     ss = a + first + " " + a + (" " + a).join(mm[0][1:])
#     print(ss.split(" "))

@renderable()
def epl1(r):
    ri = r%"Caƒ100ƒa/@1/Raƒ200ƒa/@1"
    dps = DPS().constants(ri=ri, cf=0.65)

    #return dps.ep("$ri↗↘").s(0)

    a = dps.ep("$ri↗↘ ↙|$cf|#/OX-50← ↖|$cf|#↗").f(0).pens[0]
    b = DP().mt(ri.pne).lt(ri.pse).bct((ri/-50).pw, "SW", dps.c.cf+0.1).bct(ri.pne, "NW", dps.c.cf+0.1).cp().f(0)

    return DPS([
        DP().gridlines(r, 100, absolute=1),
        DP(ri).f(hsl(0.7, a=0.1)),
        a.copy().xor(b).f(hsl(0.3)),
        a.copy().union(b).f(0, 0.1),
        #DP(ri.e("↗")).s(hsl(0.5))
        #DP(r%"Caƒ100ƒa/@1/⊢/OY100"),
        #DP(r%"I100/SY+100/MX-200/—/OY100"),
        #(DP(r.inset(100).subtract(100, "mxy").setmnx(200).ecy.offset(0, 100)).s(0, 0.2).sw(10)),
    ])