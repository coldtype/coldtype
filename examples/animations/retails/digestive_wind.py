from coldtype import *
import noise

# available from https://ohnotype.co/fonts/digestive
# though other variable-wdth faces can be substituted
df = Font.Find("DigestiveVariable")
t = Timeline(180, storyboard=[0])

# TODO must be a way to speed this way up by inferring a height axis from the width

def style_a(f, hit):
    ps:PS = (StSt("Digestive", df, 300+30*(1-hit),
        wdth=0, ro=1, t=-10*(1-hit))
        .align(f.a.r))
    
    def alter(idx, p):
        fr = p.ambit()
        rng = 10+45*hit
        factor = 0.05
        x_seed = (f.i+idx)*factor
        fs = (200-rng)+noise.pnoise1(x_seed, repeat=int(t.duration*factor))*rng
        if p.glyphName != "space":
            return StSt(p.glyphName, df, fs, wdth=1, ro=1, fit=fr.w).align(fr)[0]
        else:
            return P()
    
    return ps.map(alter)

@animation(rect=(1200,300), timeline=t, bg=0)
def render(f):
    return style_a(f, 1).f(1)