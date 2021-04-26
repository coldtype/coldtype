from coldtype.test import *

@test()
def auto_center(r):
    return ((ß:=DPS())
        .define(
            r=r,
            nx=100,
            a="$rIX100SY+200")
        .gs("$a↙ $a↖OX+$nx|65|$a↑ $a↗OX-$nx|65|$a↘ ɜ")
        .f(None).s(0).sw(4)
        .append(StyledString("Coldtype Cdelopty".upper(),
            Style(co, 100, wdth=0.5))
            .pens()
            .distribute_on_path(ß[0], center=-5)
            .f(hsl(0.9)))
        .align(r))