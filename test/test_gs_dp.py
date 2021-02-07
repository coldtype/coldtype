from coldtype import *
from coldtype.gs import gs

assert(gs("↗|65|10|↑") == [["NE", 65, 10, "N"]])

@renderable((500, 500))
def test1(r):
    return (DPS()
        .constants(ri=r.inset(50))
        .guide(
            aƒbƒc="$riC50—a—50",
            an="&a⊤",
            cs="&c⊥",
            acp="∫ &an⍺⍵ &cs⍵⍺")
        .gss("&acp⊢ &acp⊣ &acp⊣µ")
        .f(None).s(0).sw(4))

@renderable((500, 500))
def test2(r):
    return (DPS()
        .constants(ri=r.inset(50))
        .guide(
            _ƒxƒyƒzƒ_="$riIY50C100—50—a—50—100",
            d1="&x⊥∮&z⊤")
        .gss("""$ri⊢∮~($ri↗⨝$ri↘OX-100)
            &d1⊣∮〱OX-30""")
        .f(None).s(0).sw(4))