from coldtype import *

@renderable((500, 500))
def test1(r):
    return (DPS()
        .define(
            ri=r.inset(50),
            aƒbƒc="$riC50—a—50",
            an="$a⊤",
            cs="$c⊥",
            acp="($an⍺)⫎($cs⍵)")
        .gss("$acp¶π0,50⊢ $acp⊣ $acp⊣µ")
        .f(None).s(0).sw(4))

@renderable((500, 500))
def test2(r):
    return (DPS()
        .define(
            ri=r.inset(50),
            _ƒxƒyƒzƒ_="$riIY50C100—50—a—50—100",
            d1="$x⊥∮$z⊤")
        .gss("""$ri⊢∮~($ri↗⨝$ri↘OX-100)
            $d1⊣∮〱OX-30""")
        .f(None).s(0).sw(4))

@renderable((500, 500))
def test3(r):
    def sqc(c, cc):
        return f"""{c}↑
            ↗|{cc}_|{c}→
            ↘|{cc}~|{c}↓
            ↙|{cc}_|{c}←
            ↖|{cc}~|{c}↑"""
    
    return (DPS()
        .record(StyledString("o", Style("~/Type/fonts/fonts/vulf/VulfMonoRegular.otf", 700)).pen().align(r, tv=1))
        .define(
            r=r,
            ri="$rI-8",
            c="$riI53,80",
            ic="$riI122,138",
            c3=Geo(68, 59),
            c4=Geo(63, 67))
        .gs(sqc("$c", "$c3"))
        .gs(sqc("$ic", "$c4")+" Я")
        .skel())