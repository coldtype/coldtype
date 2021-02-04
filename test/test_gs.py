from coldtype.test import *
from coldtype.gs import gs, gshphrase

@renderable((500, 500))
def test(r):
    return (DPS()
        .constants(ri=r.inset(50))
        .gss("""
            $ri $ri𝓘50⌶∩$ri𝓘100⊤
            $ri𝓣Y=0.5𝓘X75𝓒20—a—10@1⊥⍺
            $ri𝓘75↖⨝$ri↘〻𝓞X-50 ■𝓘50""")
        .f(None).s(0).sw(4))

@renderable((500, 500))
def test2(r):
    return (DPS()
        .constants(r=r.inset(50), cf="65")
        .gs("""$r←↓↑ $r↓|45|$r→
            ↙|$cf|$r↑
            $r→|$cf+10|$r↓OX-130 ɜ""")
        .f(hsl(0.9,l=0.8)).s(0).sw(4)
        .register(a="$r↖⨝$r↘", b="$rＨ∩&a")
        .realize())

@renderable((500, 500))
def test3(r):
    return (DPS()
        .constants(r=r.inset(180))
        .gs("$r← $r↑|x:=335|$r→ $r↓|x|$r←")
        .f(hsl(0.7, l=0.9)).s(0).sw(4))

@renderable((500, 500))
def test4(r):
    return (DPS()
        .constants(r=r.inset(150))
        .gss("x:=$r⊣ y:=xOX50 ($r⊤∩(y))OY25")
        .f(None).s(0).sw(4))