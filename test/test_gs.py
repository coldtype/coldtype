from coldtype.test import *

@renderable((500, 500))
def test(r):
    return (DPS()
        .define(ri=r.inset(50))
        .gss("""
            $ri
            $riI50⌶∩$riI100⊤
            $riTY=0.5IX75C20—a—10@1⊥⍺
            $riI75↖⨝$ri↘〻OX-50""")
        .f(None).s(0).sw(4))

@renderable((500, 500))
def test2(r):
    return (DPS()
        .define(r=r.inset(50), cf="65")
        .gs("""$r←↓↑ $r↓|45|$r→
            ↙|$cf|$r↑
            $r→|$cf+10|$r↓OX-130 ɜ""")
        .f(hsl(0.9,l=0.8)).s(0).sw(4)
        .define(
            a="$r↖⨝$r↘",
            b="($rＨ∩$a)OX100OY100")
        .gss("$a $b"))

@renderable((500, 500))
def test3(r):
    return (DPS()
        .define(r=r.inset(180))
        .gs("$r← $r↑|x:=335|$r→ $r↓|x|$r←")
        .f(hsl(0.7, l=0.9)).s(0).sw(4)
        .rotate(90))

@renderable((500, 500))
def test4(r):
    return (DPS()
        .define(r=r.inset(150))
        .gss("x:=$r⊣ y:=xOX50 ($r⊤∩(y))OY50")
        .gs("(r:=$rI-20)↖ ↙↗|175|r↓")
        .f(None).s(0).sw(4))