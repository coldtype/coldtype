from coldtype import *

ppvf = Font.Find("PappardelleParty-VF")

custom_palette = [
    hsl(0.35, 0.7),
    hsl(0.5, 0.7),
    hsl(0.1, 0.7),
    hsl(0.9, 0.7)
]

def spin(fa, g):
    y = 100
    # address color font layers individually
    g[2].translate(0, fa.e(1, rng=(0, y)))
    g[0].translate(0, fa.e(1, rng=(0, -y)))
    g[1].rotate(fa.e(0, rng=(0, -360*2)))

@animation((1080, 1080), timeline=120)
def pappardelle(f):
    wave = (StSt("SPIN", ppvf, 500,
        palette=custom_palette,
        #palette=1,
        SPIN=f.e("l", 0))
        .align(f.a.r))

    r_wave = wave.ambit(tx=1, ty=1)
    
    return P(
        P(r_wave.inset(-20, -15)).f(None).s(custom_palette[2]).sw(3),
        (wave.copy()
            .map(lambda i, p: spin(f.adj(-i*4), p))
            .rotate(f.e(0, to1=1)*360, point=r_wave.pc)))