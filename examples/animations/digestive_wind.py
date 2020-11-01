from coldtype import *
import noise

# available from https://ohnotype.co/fonts/digestive
# though other variable-wdth faces can be substituted
df = "~/Type/fonts/fonts/_wdths/DigestiveVariable.ttf"

t = Timeline(180, storyboard=[0])

def style_a(f, hit):
    dps:DATPenSet = StyledString("Digestive", Style(df, 300+30*(1-hit), wdth=0, ro=1, t=-10*(1-hit))).pens().align(f.a.r)
    def alter(idx, p):
        fr = p.getFrame()
        rng = 10+45*hit
        factor = 0.05
        x_seed = (f.i+idx)*factor
        fs = (200-rng)+noise.pnoise1(x_seed, repeat=int(t.duration*factor))*rng
        if p.glyphName != "space":
            return StyledString(p.glyphName, Style(df, fs, wdth=1, ro=1)).fit(fr.w).pens().align(fr)[0]
        else:
            return DATPen()
    return dps.map(alter)

@animation(rect=(1200,300), timeline=t)
def render(f):
    return DATPenSet([
        DATPen().rect(f.a.r).f(0),
        style_a(f, 1).f(1)
    ])