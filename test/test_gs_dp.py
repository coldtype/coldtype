from coldtype import *
from coldtype.gs import gs

print(gs("↗|65|10|↑"))

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
    return (DPS().constants(ri=r.inset(50))
        .gss("$ri⊢∮~($ri↗⨝$ri↘OX-100)")
        .f(None).s(0).sw(4))