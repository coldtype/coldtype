from coldtype import *
from coldtype.raster import *

drums = MidiTimeline(ººsiblingºº("media/cyber.mid"), bpm=100, fps=30)

wav = download("https://coldtype.xyz/examples/media/cyber.wav", ººsiblingºº("media/cyber.wav"))

@animation((1080, 1350)
    , timeline=drums
    , audio=wav
    , bg=hsl(0.95, 0.70, 0.55)
    , release=λ.export("h264", True, 4))
def pixels(f):
    def pixellate(idx, note, i, o, max, min):
        def _pixellate(p:P):
            value = drums.ki(note).adsr([i, o]
                , ["cei", "ceo"]
                , r=(max, min))
            return p.index(idx, lambda _p: _p
                .ch(precompose(f.a.r, scale=value)))
        return _pixellate
    
    return (P(
        StSt("pixels\npixels\npixels", Font.JBMono()
            , fontSize=160
            , wght=0.75
            , wdth=1
            , opsz=0)
            .f(1)
            .lead(60)
            .align(f.a.r, "C", ty=1)
            .mape(lambda e, line: line
                .declare(m:=e*0.0025)
                .index([1, 1], lambda p: p.t(0, drums.ki(42).adsr(r=(0, 40))))
                .ch(pixellate(0, 36, 3, 40, 0.15-m, 0.01-m))
                .ch(pixellate(2, 38, 3, 30, 0.15-m, 0.02-m))
                .ch(pixellate(1, 42, 5, 20, 0.35-m, 0.05-m))
                .ch(pixellate(3, 47, 5, 20, 0.15-m, 0.0125-m))
                .ch(pixellate(4, 45, 5, 20, 0.15-m, 0.0125-m))
                .ch(pixellate(5, 39, 5, 20, 0.15-m, 0.0125-m)))
            .index(1, λ.ch(phototype(f.a.r, 1, 90, 60, fill=1)))
            .index(2, λ.ch(phototype(f.a.r, 5, 150, 30, fill=1)))))