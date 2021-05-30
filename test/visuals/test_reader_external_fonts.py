from coldtype.test import *

@test()
def test_family_narrowing(r):
    style = Style("≈/nikolai/Nikolai-Bold.otf", 200, narrower=Style("≈/nikolai/Nikolai-NarrowBold.otf", 200, narrower=Style("≈/nikolai/Nikolai-CondBold.otf", 200)))
    out = DATPens()
    rs = r.inset(0, 40).subdivide(3, "mxy")
    out += StyledString("Narrowing", style).pens().align(rs[0])
    out += StyledString("Narrowing", style).fit(r.w-100).pens().align(rs[1])
    out += StyledString("Narrowing", style).fit(r.w-200).pens().align(rs[2])
    return out


@test()
def test_stroke_ufo(r):
    hershey_gothic = Font("≈/hershey/Hershey-TriplexGothicGerman.ufo")
    hershey_gothic.load()
    return StyledString("Grieß".upper(), Style(hershey_gothic, 200, tu=-100)).pens().f(None).s("hr", 0.5, 0.5).sw(3).align(r)


@test()
def test_emoji(r):
    emoji = StyledString("🍕💽🖥", Style("assets/TwemojiMozilla.ttf", 300, t=20, ch=500, bs=11)).pens().align(r)
    #print(emoji.layered)
    return emoji


@test()
def test_color_font(r):
    out = DATPens()
    for x in reversed(range(0, 6)):
        out += StyledString("COLDTYPE", Style("≈/PappardelleParty-VF.ttf", 550, palette=x)).pens().translate(x*10, x*10)
    return out.align(r)


@test()
def test_language(r):
    """Should have an accent over the j"""
    style = Style("assets/SourceSerifPro-Black.ttf", 350, wdth=1, wght=1, ss01=True)
    return StyledString("ríjks", style.mod(lang="NLD")).pen().align(r)