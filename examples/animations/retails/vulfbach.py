from coldtype import *
from coldtype.fx.skia import color_phototype

"""
Run as `coldtype examples/animation/vulfbach.py`
To multiplex, add ` -m` to the end of that call
(then when you hit `a` in the viewer app, the frames
will render in parallel in random-order)

Rendered with organ.wav as the backing track:
    https://vimeo.com/489013931/cd77ab7e4d
"""

midi = MidiTimeline(
    "examples/animations/media/organ.mid"
    , bpm=183, fps=30)

note_width = 3
r = Rect(1440, 1080)

def pos(x, y):
    y = int(y)
    return (x*note_width, (y-midi.min)*(r.h-200)/midi.spread+100)

def build_line():
    dp = P().f(None).s(rgb(1, 0, 0.5)).sw(3)
    last:Timeable = None

    for t in midi.timeables:
        if last and (t.start - last.end > 3 or last.name == t.name):
            dp.lineTo((pos(last.end, last.name)))
            dp.endPath()
            last = None
        
        if last:
            if last.end < t.start:
                dp.lineTo((pos(last.end, last.name)))
            else:
                dp.lineTo((pos(t.start, last.name)))
            dp.lineTo((pos(t.start, t.name)))
        else:
            dp.moveTo((pos(t.start, t.name)))
        
        last = t
    
    if last:
        dp.lineTo((pos(last.end, int(last.name))))
    dp.endPath()
    return dp

line = build_line()

@animation(timeline=midi, rect=r)
def render(f):
    time_offset = -f.i * note_width + r.w - note_width * 3
    time_offset += 10 # fudge
    looped_line = P(
        (line.copy()
            .translate(
                time_offset - f.t.duration * note_width,
                0)),
        (line.copy()
            .translate(time_offset, 0)))

    return (P(
        P().rect(f.a.r).f(0),
        (looped_line.pen()
            .ch(color_phototype(f.a.r, blur=20, cut=215, cutw=40))),
        (looped_line.pen()
            .ch(color_phototype(f.a.r, blur=3, cut=200, cutw=25)))))