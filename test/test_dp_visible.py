from coldtype.test import *

@test(bg=1)
def mixed_visibility(r):
    dp = (DATPen()
        .oval(r.inset(50).square())
        .f(0.8)
        .v(1)
        .tag("circle"))
    dps = DATPenSet([dp]).v(1)
    dps2 = DATPenSet([
        dps,
        DATPen().oval(r.square()).f(hsl(0.3, a=0.25))
    ]).v(1)
    dps3 = DATPenSet([dps2])
    return dps3.v(1)