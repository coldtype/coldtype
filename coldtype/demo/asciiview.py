from coldtype import *
from coldtype.tool import parse_inputs
from collections import defaultdict

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    ascii=[None, str, "Must provide AsciiTimeline"]))

at:AsciiTimeline = args["ascii"]

lh = 60
lt = 40

lines = defaultdict(lambda: [])
for t in at.enumerate():
    lines[t.data["line"]].append(t)

def build_display(r):
    wu = r.w / int(at.duration)
    rows = r.subdivide(len(lines), "N")

    out = PS()
    for line in lines.keys():
        out += (P(rows[line - 1].take(2, "N"))
            .f(bw(0.8))
            .t(0, 1))
        out += (StSt(str(line), Font.RecursiveMono(), 22)
            .align(rows[line - 1].inset(-80, 0), "W"))

    for t in at.enumerate():
        l = int(t.data["line"])-1
        f = hsl(0.5+l*0.3)
        row = rows[l]
        tr = (row.take(t.duration*wu, "W")
            .offset(t.start*wu, 0))
        
        out += (P(tr).f(f.lighter(0.2)))
        out += (P(row.take(2, "W"))
            .translate(t.start*wu, 0)
            .f(f))
        out += (StSt(t.name, Font.RecursiveMono(), 38)
            .align(row.take(20, "W"), "W")
            .translate(t.start*wu+6, 0)
            .f(f.darker(0.15)))

    return out

r = Rect(1080, len(lines)*lh+lt)
rw, re = r.divide(100, "W")
rt, rd = re.divide(lt, "N")
display = build_display(rd)

@animation(r, timeline=at, bg=1, preview_only=1)
def asciiview(f):
    return PS([
        P(rw).f(bw(0.95)),
        P(rt).f(bw(0.95)),
        #P(rt.take(2, "S")).f(0.8),
        display,
        (P(Rect(2, r.h))
            .t(f.e("l", 0, rng=(rd.psw[0], rd.pse[0])), 0))])