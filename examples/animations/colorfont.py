from coldtype import *

fnt1 = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")
fnt = Font.Cacheable("~/Type/fonts/fonts/PappardelleParty-VF.ttf")

@animation((1080, 1920), bg=1)
def pappardelle(f):

    wave = (StyledString("wave",
        Style(fnt, 700, palette=0))
        .pens()
        .align(f.a.r)
        )
    
    #print(wave.tree())
    print(wave[0].ambit(th=1))

    return DPS([
        DP(wave.ambit(th=1).inset(-10, -10)).f(None).s(0).sw(5),
        wave,
        wave.frameSet()
    ]).align(f.a.r)#.translate(200, 200)