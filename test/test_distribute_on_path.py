from coldtype.test import *

@test()
def auto_center(r):
    return ((ß:=DPS([r]))
        .constants(nx=100)
        .guide(
            a="□I100",
            c="∫ &a↙ &a↖OX+$nx|65|&a↑ &a↗OX-$nx|65|&a↘")
        .append(ß._guides.c)
        .f(None).s(0).sw(4)
        .append(StyledString("Coldtype Cdelopty".upper(),
            Style(co, 100, wdth=0.5))
            .pens()
            .distribute_on_path(ß._guides.c, center=-5)
            .f(hsl(0.9))))