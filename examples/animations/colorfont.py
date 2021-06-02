from coldtype import *

ppvf = Font.Cacheable("~/Type/fonts/fonts/PappardelleParty-VF.ttf")

def spin(fa, g):
    y = 100
    # address color font layers individually
    #g[2].translate(0, fa.e(1, rng=(0, y)))
    #g[0].translate(0, fa.e(1, rng=(0, -y)))
    #g[1].rotate(fa.e(rng=(0, -360*2)))

@animation((1080, 1920), timeline=120)
def pappardelle(f):
    wave = (StSt("SPIN", ppvf, 500,
        palette=0, _SPIN=f.e("l"))
        .align(f.a.r.take(0.4, "mny")))

    r_wave = wave.ambit(th=1, tv=1)

    for idx, g in enumerate(wave):
        spin(f.adj(-idx*4), g)
    
    return wave#.rotate(f.e(to1=1)*360, point=r_wave.pc)