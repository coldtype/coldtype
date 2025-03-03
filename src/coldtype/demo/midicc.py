from coldtype import *
from coldtype.tool import parse_inputs

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    port=[None, str, "Must provide port name"],
    channel=[1, int]))

r = args["rect"]

@animation(r,
    bg=0,
    rstate=1,
    preview_only=args["preview_only"])
def midicc(f, rs):
    if 0:
        print(rs.midi)

    controls = []

    for k, v in rs.midi.items():
        for c, data in v.items():
            for note, value in data.items():
                if not note.startswith("_"):
                    controls.append([k, c, note, value])
    
    rs = f.a.r.subdivide(len(controls), "W")

    def show_cc(x):
        _r = rs[x.i].inset(1)
        k, c, note, value = x.el
        return P(
            P(_r).f(hsl(0.9, 0.7, 0.8)),
            StSt("A", Font.MuSan(), 100, wdth=value/127, wght=value/127).align(_r),
            P(
                StSt(str(value), Font.RecMono(), 42),
                StSt(note, Font.RecMono(), 52),
                StSt(f"{k} / 1", Font.RecMono(), 24),
            )
            #.map(lambda p: p.scaleToWidth(_r.w, shrink_only=1))
            .xalign(_r, "W", tx=0)
            .align(_r)
            .stack(10)
            .align(_r.inset(0), "SW", tx=0, ty=0)
        )

    return P().enumerate(controls, show_cc)