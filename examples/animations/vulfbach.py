from coldtype import *
from coldtype.animation.midi import MidiReader

midi = MidiReader("examples/animations/media/organ.mid", bpm=183, fps=30)
organ = midi[0]

note_width = 3
r = Rect(1440, 1080)

def pos(x, y):
    return (x*note_width, (y-midi.min)*(r.h-200)/midi.spread+100)

def build_line():
    dp = DATPen().f(None).s(1, 0, 0.5).sw(3)
    last_note = None

    for note in organ.notes:
        if last_note and (note.on - last_note.off > 3 or last_note.note == note.note):
            dp.lineTo((pos(last_note.off, last_note.note)))
            dp.endPath()
            last_note = None
        if last_note:
            if last_note.off < note.on:
                dp.lineTo((pos(last_note.off, last_note.note)))
            else:
                dp.lineTo((pos(note.on, last_note.note)))
            dp.lineTo((pos(note.on, note.note)))
        else:
            dp.moveTo((pos(note.on, note.note)))
        last_note = note
    if last_note:
        dp.lineTo((pos(last_note.off, last_note.note)))
    dp.endPath()
    return dp

line = build_line()

@animation(duration=organ.duration, rect=r, storyboard=[50])
def render(f):
    return DATPenSet([
        line.copy().translate(-f.i*note_width+r.w-note_width*3-organ.duration*note_width, 0),
        line.copy().translate(-f.i*note_width+r.w-note_width*3, 0)
    ])