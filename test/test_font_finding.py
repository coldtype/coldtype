from coldtype.animation import *

def render(f):
    outline = 15
    s = Style("≈/Obviously", 500, fill=1, tu=-70, wdth=0.47, wght=1, slnt=1, ss01=1, overlap_outline=outline, kern_pairs={("C.alt","O"):-20, ("O","L"):-63, ("T","Y"):-90, ("Y","P"):5, ("P","E"):-247}, r=1, ro=1)
    dps = Graf(T2L("COLD\nTYPE", s), f.a.r.inset(90, 0), leading=20).fit().pens().interleave(lambda p: p.outline(outline).f(0) if p.glyphName else p).scale(0.85, center=False).å(f.a.r)
    dps[0].translate(-20, -10)
    dps[1].translate(20, 10)
    return DATPen().oval(f.a.r.inset(20, 20)).f(0), dps.reversePens()

animation = Animation(render, (1080, 1080), bg=(0, 0))