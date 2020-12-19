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
        DATPen().gridlines(r).s(0, 0.1).sw(1)
    ])
    dps2.v(0)
    dps2.print_tree()
    print("----------------")
    return DATPenSet([dps2])