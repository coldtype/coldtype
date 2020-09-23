from coldtype.test import *


@test()
def test_fit(r):
    inset = 150
    return [
        DATPen().rect(r.inset(inset, 0)).f("hr", 0.5, 0.9),
        Slug("COLD", Style(co, 500, wdth=1, wght=1, slnt=1, tu=-150, r=1)).fit(r.w-inset*2).pens().f("random").align(r).understroke()
    ]


@test()
def test_style_mod(r):
    style = Style(co, 250, wdth=1)
    out = DATPenSet()
    out += StyledString("CLDTP", style).pen()
    out += StyledString("CLDTP", style.mod(wdth=0)).pen()
    return out.rp().distribute(v=1).track(10, v=1).align(r).f("hr", 0.5, 0.5)


@test()
def test_fit_height(r):
    style = Style(co, 150, wdth=1)
    out = DATPenSet()
    out += StyledString("CLDTP", style).pen()
    out += StyledString("CLDTP", style.mod(fitHeight=300)).pen()
    return out.rp().distribute(v=1).track(10, v=1).align(r).f("hr", 0.5, 0.5)


@test()
def test_interp(r):
    count = 30
    out = DATPenSet()
    for x in range(count):
        style = Style(co, 200, wdth=x/count, ro=1)
        out += StyledString("COLDTYPE", style).pens().f("random", 0.1).s(0, 0.1).sw(2).align(r).translate(0, x).rotate(x*0.5)
    return out


@test()
def test_kern_pairs(r):
    return StyledString("CLD", Style(co, 300, rotate=-10, kp={"C/L":20, "L/D":45})).pens().align(r).f("hr", 0.65, 0.65)


@test()
def test_family_narrowing(r):
    style = Style("≈/nikolai/Nikolai-Bold.otf", 200, narrower=Style("≈/nikolai/Nikolai-NarrowBold.otf", 200, narrower=Style("≈/nikolai/Nikolai-CondBold.otf", 200)))
    out = DATPenSet()
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
    print(emoji.layered)
    return emoji


@test()
def test_color_font(r):
    out = DATPenSet()
    for x in reversed(range(0, 6)):
        out += StyledString("COLDTYPE", Style("≈/PappardelleParty-VF.ttf", 550, palette=x)).pens().translate(x*10, x*10)
    return out.align(r)


@test()
def test_language(r):
    """Should have an accent over the j"""
    style = Style("assets/SourceSerifPro-Black.ttf", 350, wdth=1, wght=1, ss01=True)
    return StyledString("ríjks", style.mod(lang="NLD")).pen().align(r)

@test()
def test_xstretch(r):
    st = Style.StretchX(20, debug=1,
        A=(200, 230),
        B=(1500, 190),
        C=(200, 290))
    style = Style(mutator, 500, mods=st, wght=0.25)
    return (StyledString("ABC", style)
        .pen()
        .align(r)
        .scale(0.5)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2))

@test()
def test_xstretch_slnt(r):
    st = Style.StretchX(20, debug=1,
        L=(500, (400, 750/2), -14),
        O=(1000, (385, 750/2), -14))
    style = Style(co, 500, mods=st)
    return (StyledString("LOL", style)
        .pen()
        .align(r)
        .scale(0.5)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2))

@test()
def test_ystretch(r):
    st = Style.StretchY(20, debug=1,
        E=(500, 258))
    print(st)
    style = Style(mutator, 300, mods=st, wght=0.5)
    return (StyledString("TYPE", style)
        .pen()
        .align(r, th=1, tv=1)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2))

@test()
def test_ystretch_slnt(r):
    st = Style.StretchY(20, debug=1,
        E=(500, (258, 750/2), 25))
    style = Style(co, 300, mods=st, wght=0.5)
    return (StyledString("TYPE", style)
        .pen()
        .align(r, th=1, tv=1)
        .f(hsl(0.2, a=0.1))
        .s(hsl(0.5))
        .sw(2)
        #.removeOverlap()
        )