from coldtype import *
from coldtype.blender import *
from coldtype.fx.skia import potrace

chars = "ABCDEFGHIJKLMNOPQRSTUVWYXZ"

@b3d_animation(timeline=len(chars), center=(0, 0))
def letters(f):
    return (StSt(chars[f.i], Font.Find("Degular-Bo"), 1000, wght=0.5)
        .f(1)
        .pen()
        .align(f.a.r, tx=0)
        .ch(b3d(lambda bp: bp
            .extrude(0.01)
            .rotate(-15))))

ufo = quick_ufo(__sibling__("fonts/letters1.ufo"), "Perspective")

@animation(timeline=letters.t, solo=1, bg=1)
def letters_potrace(f):
    glyph_name = chars[f.i]

    original = letters.func(f).f(hsl(0))
    oframe = original.ambit(tx=0, ty=0)

    yoffset = 61
    xscale = 1.16
    xpad = 20
    
    mod_frame = (P(oframe.zero())
        .scale(xscale, 1, pt=(0,0))
        .ambit().add(xpad*2, "E"))
    
    mod = (P(f.a.r)
        .img(letters.frameImg(f.i), f.a.r)
        .ch(potrace(f.a.r))
        .t(0, yoffset)
        .f(hsl(0.5, a=0.5))
        .data(frame=oframe)
        .zero()
        .scale(xscale, pt=(0,0))
        .translate(xpad, 0)
        .data(frame=mod_frame))
    
    mod_glyph = mod.toGlyph(glyph_name, width=mod_frame.w)
    mod_glyph.unicode = glyph_to_uni(glyph_name)
    ufo.insertGlyph(mod_glyph)
    ufo.save()

    return (P(
        original.zero(),
        P(original.ambit()).fssw(-1, 0, 2),
        mod,
        P(mod.ambit()).fssw(-1, 0, 2),
        ).t(50, 50))