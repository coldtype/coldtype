from collections import defaultdict
from coldtype.renderable.animation import animation, renderable
from coldtype.text.composer import StSt, Font, Rect, Point, Style
from coldtype.time.timeline import Timeline
from coldtype.time.midi import MidiTimeline
from coldtype.runon.path import P
from coldtype.color import bw, hsl

from coldtype.runon.path import P as P

PS = P

def timeViewer(tl):
    a = None
    ow = 1080

    if isinstance(tl, animation):
        a = tl
        tl = a.t
        ow = a.rect.w

    lh = 40
    lt = 40

    lines = defaultdict(lambda: [])

    if False and isinstance(tl, MidiTimeline):
        for n in tl.notes:
            lines[n].append(n)
    elif isinstance(tl, Timeline):
        lines = tl.tracks()
    else:
        lines[0] = 1
    
    try:
        line_count = max(lines.keys())+1
    except ValueError:
        line_count = 0

    def build_timeable_display(r):
        wu = r.w / int(tl.duration)
        rows = r.subdivide(line_count, "N")
            
        out = PS()
        fs = 14
        
        for line in lines.keys():
            out += (P(rows[line].take(2, "N"))
                .f(bw(0.8))
                .t(0, 1))
            out += (StSt(str(line),
                Font.RecursiveMono(), fs)
                .align(rows[line].inset(-12, 0), "W")
                .f(hsl(0.65, 1, 0.7)))
            out += (StSt(str(line),
                Font.RecursiveMono(), fs)
                .align(rows[line].inset(-12, 0), "E")
                .f(hsl(0.65, 1, 0.7)))

        for t in tl.timeables:
            l = int(t.track)
            f = hsl(0.5+l*0.3)
            row = rows[l]
            tr = (row.take(t.duration*wu, "W")
                .offset(t.start*wu, 0))
            
            out += (P(tr).f(f.lighter(0.2).with_alpha(0.8)))
            out += (P(row.take(2, "W"))
                .translate(t.start*wu, 0)
                .f(f))
            out += (StSt(t.name,
                Font.RecursiveMono(), 34)
                .align(row.take(20, "W"), "W")
                .translate(t.start*wu+6, 0)
                .f(f.darker(0.15)))

        return out

    r = Rect(ow, line_count*lh+lt)
    re = r.inset(20, 0)
    rt, rd = re.divide(lt, "N")

    if isinstance(tl, Timeline):
        display = build_timeable_display(rd)
    else:
        display = PS()

    outer = PS([
        #P(rw).f(bw(0.95)),
        P(rt).f(bw(0.95))
        ])

    frames = re.subdivide(tl.duration, "W")
        
    for idx, f in enumerate(frames):
        if idx%2==1:
            continue
        outer += (P(f).f(bw(0.9)))

    outer += display

    @renderable(r, xray=False, bg=1)
    def timeViewBackground(r):
        return outer

    @animation(r
    , timeline=tl
    , bg=1
    , preview_only=1
    , sort=-1
    , layer=1
    , offset=a.offset
    , xray=False
    )
    def timeView(f):
        x = f.e("l", 0, rng=(rd.psw[0], rd.pse[0]))
        return PS([
            P(Rect(2, r.h)).t(x, 0),
            (P().text(str(f.i),
                Style("Times", 20, load_font=0),
                Rect(x+6, r.h-20, 100, 40)))])
    
    def pointToFrame(pt:Point):
        return round(min(1, max(0, (pt.x-re.x)/re.w))*tl.duration)
    
    timeView.pointToFrame = pointToFrame
    return timeViewBackground, timeView