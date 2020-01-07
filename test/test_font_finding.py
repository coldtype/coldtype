from coldtype.animation import *

def render(f):
    outline = 15
    font = "ç/variable_ttf/ColdtypeObviously-VF.ttf"
    text = ["COLD", "TYPE"]
    kp = {("C","O"):-40, ("O","L"):-63, ("T","Y"):-90, ("Y","P"):-20, ("P","E"):-247}
    s = Style(font, 500, fill=1, tu=-70, wdth=0.9, overlap_outline=outline, kern_pairs=kp, r=1, ro=1)
    graf = Graf([Slug(t, s) for t in text], f.a.r.inset(90, 0), leading=20)
    graf.fit()
    dps = graf.pens().interleave(lambda p: p.outline(outline).f(0) if p.glyphName else p).scale(0.85, center=False).å(f.a.r)
    dps[0].translate(-20, -10)
    dps[1].translate(20, 10)
    return DATPen().oval(f.a.r.inset(20, 20)).f(0), dps.reversePens()

animation = Animation(render, (1080, 1080), bg=(0, 0))