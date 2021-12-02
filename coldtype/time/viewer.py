from collections import defaultdict
from coldtype.renderable.animation import animation, renderable
from coldtype.text.composer import StSt, Font, Rect, Point, Style
from coldtype.time.midi import MidiTimeline
from coldtype.time.nle.ascii import AsciiTimeline
from coldtype.pens.datpen import P, PS, DATText
from coldtype.color import bw, hsl


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

    if isinstance(tl, AsciiTimeline):
        for t in tl.enumerate():
            lines[t.data["line"]].append(t)
    elif isinstance(tl, MidiTimeline):
        for n in tl.notes:
            lines[n].append(n)
    else:
        lines[0] = 1

    def build_midi_display(r):
        wu = r.w / int(tl.duration)
        rows = r.subdivide(len(lines), "N")
        
        out = PS()
        
        for idx, line in enumerate(lines.keys()):
            out += (P(rows[idx].take(2, "N"))
                .f(bw(0.8))
                .t(0, 1))
        
        for t in tl.timeables:
            l = tl.notes.index(int(t.name))
            f = hsl(0.5+l*0.3)
            row = rows[l]
            tr = (row.take(t.duration*wu, "W")
                .offset(t.start*wu, 0))
            
            out += (P(tr).f(f.lighter(0.2).with_alpha(0.8)))

            out += (P(row.take(2, "W"))
               .translate(t.start*wu, 0)
               .f(f))
            out += (StSt(t.name, Font.RecursiveMono(), 32)
               .align(row.take(20, "W"), "W", tv=1)
               .translate(t.start*wu+6, 0)
               .f(f.darker(0.15)))
        
        return out

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
            out += (StSt(t.name, Font.RecursiveMono(), 34)
                .align(row.take(20, "W"), "W")
                .translate(t.start*wu+6, 0)
                .f(f.darker(0.15)))

        return out

    r = Rect(ow, len(lines)*lh+lt)
    #rw, re = r.divide(100, "W")
    re = r.inset(20, 0)
    rt, rd = re.divide(lt, "N")

    if isinstance(tl, AsciiTimeline):
        display = build_ascii_display(rd)
    elif isinstance(tl, MidiTimeline):
        display = build_midi_display(rd)
    else:
        display = PS()

    outer = PS([
        #P(rw).f(bw(0.95)),
        P(rt).f(bw(0.95))])

    frames = re.subdivide(tl.duration, "W")
        
    for idx, f in enumerate(frames):
        if idx%2==1:
            continue
        outer += (P(f).f(bw(0.9)))

    outer += display

    @renderable(r)
    def timeViewBackground(r):
        return outer

    @animation(r
    , timeline=tl
    , bg=1
    , preview_only=1
    , sort=-1
    , layer=1
    )
    def timeView(f):
        x = f.e("l", 0, rng=(rd.psw[0], rd.pse[0]))
        return PS([
            P(Rect(2, r.h)).t(x, 0),
            # (StSt("{:04d}\n{:04d}"
            #     .format(f.i, f.t.duration),
            #     Font.RecursiveMono(), 22)
            #     .align(rw.inset(10), th=0))
            (DATText(str(f.i), Style("Times", 20, load_font=0), Rect(x+6, r.h-20, 100, 40))
                #.align(rw.inset(10), th=0)
                )
                ])
    
    def pointToFrame(pt:Point):
        return round(min(1, max(0, (pt.x-re.x)/re.w))*tl.duration)
    
    timeView.pointToFrame = pointToFrame
    return timeViewBackground, timeView