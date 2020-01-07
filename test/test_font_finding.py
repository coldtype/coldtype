from coldtype.animation import *

def mod_o(idx, dp):
    if dp.glyphName == "O":
        # push the counter over a little for balance
        o_outer, o_counter = dp.explode()
        return o_outer.record(o_counter.translate(20, 0))

def render(f):
    outline = 15
    s = Style("ç/variable_ttf/ColdtypeObviously-VF.ttf", 500, fill=1, tu=-70, wdth=0.9, overlap_outline=outline, kern_pairs={("C","O"):-90, ("O","L"):-78, ("T","Y"):-90, ("Y","P"):-20, ("P","E"):-247}, r=1, ro=1)
    dps = Graf([Slug(t, s) for t in ["COLD", "TYPE"]], f.a.r.inset(90, 0), leading=10).fit().pens().reversePens().mmap(lambda idx, dps: dps.translate([80, -60][idx], 0)).flatten().map(mod_o).interleave(lambda p: p.outline(outline).f(0)).scale(0.93, center=False).align(f.a.r)
    return DATPen().oval(f.a.r.inset(20, 20)).f(0), dps

animation = Animation(render, (1024, 1024), Timeline(1, storyboard=[0]), bg=None)