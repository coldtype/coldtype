from coldtype import *

mt = MidiTimeline(ººsiblingºº("media/midi_cc.mid"))
wav = ººsiblingºº("media/midi_cc.wav")

fnt = Font.MutatorSans()

@animation(tl=Timeline(120, 30), bg=0, audio=wav)
def cc(f):
    mt.hold(f.i)
    #print(mt.ci(104))
    return (P(
        StSt("MIDI", fnt, 200
            , wght=0, wdth=ez(mt.ci(102), "sei", rng=(0.5, 1))),
        StSt("CC", fnt, 300
            , wght=1, wdth=ez(mt.ci(103), "eeo")),
        StSt("DATA", fnt, 100),
        )
        .stack(20)
        .xalign(f.a.r)
        .align(f.a.r)
        .index(2, lambda p: p.scale(ez(mt.ci(104), "eeo", rng=(1, 5))))
        .fssw(1, 0, 4, 1)
        .reverse())
