from coldtype import *

@renderable()
def epl1(r):
    #return (StyledString("SZ",
    #    Style("~/Type/fonts/fonts/OhnoFatfaceVariable.ttf", 500, opsz=0.75, tu=0, wdth=0.25))
    #    .pen()
    #    .align(r)
    #    .f(0))
    return DPS([
        DP(r%"I100/SY+100/MX-200/—/OY100"),
        (DP(r.inset(100).subtract(100, "mxy").setmnx(200).ecy.offset(0, 100))
            .s(0, 0.2).sw(10)),
    ])
    return None