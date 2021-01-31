from coldtype import *

def dpepl(sdp, s):
    cmds = s.split("  ")
    dp = DATPen()
    for cidx, cmd in enumerate(cmds):
        v = Rect(0, 0) % sdp.vs(cmd)
        if cidx == 0:
            dp.moveTo(v)
        else:
            dp.lineTo(v)
    dp.closePath()
    return dp

@renderable()
def epl1(r):
    ri = r%"Caƒ100ƒa/@1/Raƒ200ƒa/@1"
    dp = DP().constants(ri=ri)
    print(r%dp.vs("$ri/↗"))
    return DPS([
        DP(r).f(None).s(0).sw(4),
        dpepl(dp, "$ri/↗  $ri/↘  $ri/OX-50/←").f(0).s(0),
        #DP(r%"Caƒ100ƒa/@1/⊢/OY100"),
        #DP(r%"I100/SY+100/MX-200/—/OY100"),
        #(DP(r.inset(100).subtract(100, "mxy").setmnx(200).ecy.offset(0, 100)).s(0, 0.2).sw(10)),
    ])