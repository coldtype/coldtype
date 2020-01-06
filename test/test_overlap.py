from coldtype.animation import *

def render(f):
    if False:
        dp = StyledString("e", Style("≈/Triptych-Italick.otf", 300, wdth=0.5, wght=0.55, fill=1)).pen().align(f.a.r)
        #dp.record(dp.copy().outline(3)).removeOverlap()
        dp.record(dp.copy().outline(1).reverse().removeOverlap())
        return dp.f(None).s(1).sw(1)

    font = "meek"

    if font == "triptych":
        fn = "≈/Triptych-Italick.otf"
        t = -50
        kp = {
            ("l", "a"): (-30, 0),
            ("a", "p"): (-130, 0),
            ("r", "l"): (-100, 0),
            ("e", "r"): (-125, 0),
            ("O", "v"): (-315, 0),
            ("v", "e"): (-150, 0),
        }
    elif font == "blaze":
        fn = "≈/OhnoBlazeface18Point.otf"
        kp = {
            ("r", "l"): (50, 0)
        }
        t = -70
    elif font == "meek":
        fn = "≈/Eckmannpsych-Variable.ttf"
        t = -50
        kp = {
            #("O", "v"): (-190, 0),
            ("v", "e"): (20, 0),
            #("e", "r"): (-50, 0)
            ("a", "p"): (30, 0),
            ("O", "V"): (-10, 0),
            ("V", "E"): (-130, 0),
            ("E", "R"): (-70, 0),
            ("R", "L"): (-70, 0),
            ("L", "A"): (-50, 0)
        }

    dps = StyledString("Overlap".upper(), Style(fn, 300, fill=1, t=t, yest=0.5, kern_pairs=kp, r=1, bs=lambda idx: -5 if idx%2 == 0 else 5)).pens().align(f.a.r)#.interleave(lambda p: p.s(0).sw(6))
    dps.mmap(lambda idx, p: p.f(0.7, 0.5, 0.8) if idx%2==0 else p.f(0.8, 0.4, 0.7))
    dps.mmap(lambda idx, p: p.f(0, 1, 0) if idx%2==0 else p.f(0, 0, 1))
    #dps.mmap(lambda idx, p: p.f("random"))

    if font == "triptych":
        overlap_pair(dps, "O", "v", [1])
        overlap_pair(dps, "v", "e", [2])
        overlap_pair(dps, "e", "r", [0])
        overlap_pair(dps, "a", "p", [0])
    elif font == "nonplus":
        overlap_pair(dps, "e", "r", [0])
        overlap_pair(dps, "r", "l", [1])
        overlap_pair(dps, "l", "a", [1])
    elif font == "meek":
        dps.overlapPairs({
            ("O", "V"): [0],
            ("V", "E"): [1, 2],
            ("E", "R"): [1],
            ("R", "L"): [0],
            ("L", "A"): [0],
            ("A", "P"): [0],
        })

    dps.filter(lambda idx, p: p.getTag().startswith("overlap_outline")).mmap(lambda idx, p: p.f(0))
    dps.interleave(lambda idx, p: p.f(0).outline(3).reverse().tag(f"original_outline_{idx}") if p.glyphName else p)

    shadow = dps.copy().pen().removeOverlap().f(1, 0, 0).translate(3, -3)
    #shadow.record(shadow.copy().outline(3).reverse()).removeOverlap()
    return shadow, dps

animation = Animation(render, (1080, 1080), bg=0)