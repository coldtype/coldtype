import math
from collections import defaultdict
from coldtype.renderable.animation import animation
from coldtype.text.composer import StSt, Font, Rect, Point
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.pens.datpen import P, PS
from coldtype.color import bw, hsl


def timeViewer(tl):
    a = None
    ow = 1080

    if isinstance(tl, animation):
        a = tl
        tl = a.t
        ow = a.rect.w

    lh = 60
    lt = 40

    lines = defaultdict(lambda: [])

    if isinstance(tl, AsciiTimeline):
        for t in tl.enumerate():
            lines[t.data["line"]].append(t)
    else:
        lines[0] = 1

    def build_ascii_display(r):
        wu = r.w / int(tl.duration)
        rows = r.subdivide(len(lines), "N")
            
        out = PS()
        
        for line in lines.keys():
            out += (P(rows[line - 1].take(2, "N"))
                .f(bw(0.8))
                .t(0, 1))
            # out += (StSt(str(line),
            #     Font.RecursiveMono(), 22)
            #     .align(rows[line - 1].inset(-80, 0), "W"))

        for t in tl.enumerate():
            l = int(t.data["line"])-1
            f = hsl(0.5+l*0.3)
            row = rows[l]
            tr = (row.take(t.duration*wu, "W")
                .offset(t.start*wu, 0))
            
            out += (P(tr).f(f.lighter(0.2).with_alpha(0.8)))
            out += (P(row.take(2, "W"))
                .translate(t.start*wu, 0)
                .f(f))
            out += (StSt(t.name, Font.RecursiveMono(), 38)
                .align(row.take(20, "W"), "W")
                .translate(t.start*wu+6, 0)
                .f(f.darker(0.15)))

        return out

    r = Rect(ow, len(lines)*lh+lt)
    rw, re = r.divide(100, "W")
    rt, rd = re.divide(lt, "N")

    if isinstance(tl, AsciiTimeline):
        display = build_ascii_display(rd)
    else:
        display = PS()

    outer = PS([
        P(rw).f(bw(0.95)),
        P(rt).f(bw(0.95))])

    frames = re.subdivide(tl.duration, "W")
        
    for idx, f in enumerate(frames):
        if idx%2==1:
            continue
        outer += (P(f).f(bw(0.9)))

    outer += display

    @animation(r
    , timeline=tl
    , bg=1
    , preview_only=1
    , sort=-1
    )
    def timeView(f):
        return PS([
            outer,
            (P(Rect(2, r.h))
                .t(f.e("l", 0, rng=(rd.psw[0], rd.pse[0])), 0)),
            (StSt("{:04d}\n{:04d}"
                .format(f.i, f.t.duration),
                Font.RecursiveMono(), 22)
                .align(rw.inset(10), th=0))])
    
    def pointToFrame(pt:Point):
        return math.floor(min(1, max(0, (pt.x-re.x)/re.w))*tl.duration)
    
    timeView.pointToFrame = pointToFrame
    return timeView