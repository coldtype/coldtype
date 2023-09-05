from coldtype import *
from coldtype.blender import *

audio = __sibling__("media/simplebeat.wav")

midi = MidiTimeline(__sibling__("media/simplebeat.mid")
    , bpm=120
    , lookup={0: 36, 1: 38, 2: 40, 3: 42, 4: 45, 5: 47, 6: 48, 7: 49})

lengths = [30, 20, 20, 20, 5, 50, 30, 10]
weights = [1, 0.25, 0.25, 0.25, 0, 1, 0.5, 0]

rs = random_series()

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def prerun(bw):
    bw.deletePrevious(materials=False)

@b3d_animation((1080, 1080), timeline=midi, bg=None)
def simplebeat2(f):
    def styler(x):
        e = f.a.t.ki(x.i)
        tail = lengths[x.i]

        return [
            Style(Font.MuSan(), 300, wght=0, wdth=0.35, ital=0),
            Style(Font.MuSan()
                , fontSize=300
                , ro=1
                , wght=e.adsr([2, tail], ["sei", "ceo"]
                    , rng=(0, weights[x.i]))
                , wdth=e.adsr([2, tail], ["sei", "ceo"]
                    , rng=(0, weights[x.i])))]
    
    return (Glyphwise("MIDI\nDATA", styler)
        .lead(30)
        .xalign(f.a.r, tx=0)
        .align(f.a.r, tx=0)
        .collapse()
        .layer(
            lambda ps: ps.map(lambda i, p: p # fill
                .ch(b3d(lambda bp: bp
                    .extrude(2)
                    .locate(z=-5+5*f.a.t.ki(i)
                        .adsr([5, lengths[i]*2], ["sei", "seo"])))))))