from coldtype import *
from coldtype.raster import *
from itertools import chain

media = ººsiblingºº("media/vowels")

mt = MidiTimeline(media / "midi2.mid")
audio = media / "midi2.wav"

# https://en.wikipedia.org/wiki/IPA_vowel_chart_with_audio
# https://brill.com/page/BrillFontDownloads/Download-The-Brill-Typeface

font = Font.Find("Brill-Bold")

vowels = [
    [["i", "y"], ["ɨ", "ʉ"], ["ɯ", "u"]],
    [["ɪ", "ʏ"], ["ʊ"]],
    [["e", "ø"], ["ɘ", "ɵ"], ["ɤ", "o"]],
    [["e̞", "ø̞"], ["ə"], ["ɤ̞", "o̞"]],
    [["ɛ", "œ"], ["ɜ", "ɞ"], ["ʌ", "ɔ"]],
    [["æ"], ["ɐ"]],
    [["a", "ɶ"], ["ä"], ["ɑ", "ɒ"]],
]

flat_vowels = list(chain.from_iterable(chain.from_iterable(vowels)))

"""
not used, but a helpful snippet for processing .ogg's and .opus'es
"""
def process_wikipedia_audio():
    from pydub import AudioSegment
    for idx, vowel in enumerate(flat_vowels):
        file = Path(f"~/Downloads/_vowels/{vowel}.ogg").expanduser()
        if not file.exists():
            file = Path(f"~/Downloads/_vowels/{vowel}.opus").expanduser()

        output = ººsiblingºº(f"media/vowels/{idx}_{vowel}.wav")
        output.parent.mkdir(exist_ok=True)
        AudioSegment.from_file(file).export(output, format="wav")

#process_wikipedia_audio()

r = Rect(1080).inset(100)

close = P().m(r.pnw).l(r.pne).ep()
open = P().m(open_front:=r.drop(0.55, "W").psw).l(r.pse).ep()
front = P().m(r.pnw).l(open_front).ep()
back = P().m(r.pne).l(r.pse).ep()
central = P().m(r.pn).l(open.point_t(0.5)[0]).ep()

def xbar(t):
    return P().m(front.point_t(t)[0]).l(back.point_t(t)[0]).ep()

near_close = xbar(0.165)
close_mid = xbar(0.33)
mid = xbar(0.5)
open_mid = xbar(0.66)
near_open = xbar(0.66+0.165)

def v(c, line, t):
    return (StSt("".join(c), font, 70)
        .f(hsl(0.17, 0.80, 0.75))
        .partition(lambda p: p.data("glyphCluster"))
        .track(20)
        .align(Rect.FromCenter(line.point_t(t)[0], 1), tx=1)
        .t(0, 7)
        .layer(
            lambda p: P().rect(p.ambit(tx=1, ty=1).inset(-20)).f(0.9).tag("knockout"),
            lambda p: p.tag("symbols")
                .map(lambda i, p: p.tag("symbol").data(symbol=c[i]))))

def vs(cs, line, ts=(0, 0.5, 1.0)):
    return P().enumerate(cs, lambda x: v(x.el, line, ts[x.i]))

res = (P(
    vs(vowels[0], close),
    vs(vowels[1], near_close, [0.15, 0.85]),
    vs(vowels[2], close_mid),
    vs(vowels[3], mid),
    vs(vowels[4], open_mid),
    vs(vowels[5], near_open),
    vs(vowels[6], open)))

lines = (P(close, open, front, back, central, close_mid, open_mid)
    .outline(1)
    .difference(P(res.copy().find("knockout"))))

@animation(bg=0, tl=mt, audio=audio, release=λ.export("h264", loops=2))
def chart(f:Frame):
    r = f.a.r.inset(100)
    
    highlight = P()
    active_symbols = []
    current = 0

    for idx, symbol in enumerate(res.find("symbol")):
        if mt.ki(idx+36).on():
            highlight.append(P().oval(symbol.ambit(tx=1, ty=0).square(outside=True).inset(-20).offset(0, -5)))
            active_symbols.append(symbol.data("symbol"))
            current = idx

    return (P(
        lines.f(hsl(0.75, 0.90, 0.58))
            .chain(filmjitter(f.e("l", 4, cyclic=0), 1, scale=(1, 1))),
        highlight.fssw(-1, hsl(0.75, 1.00, 0.65, 0.8), 10),
        P(res.find("symbols"))
            .copy()
            .chain(filmjitter(f.e("l", 4, cyclic=0), 2, scale=(1, 1))),
        StSt("IPA\nvowel\nchart\nremix", font, 50)
            .align(f.a.r.inset(76, 90), "SW")
            .f(hsl(0.17, 0.80, 0.75))
            .skew(current/len(flat_vowels)/2, 0),
        StSt("".join(active_symbols[:1]), font, 920)
            .align(r.drop(0, "E"), "C", ty=0)
            #.fssw(1, hsl(0.75, 0.8, 0.6), 2)
            #.f(hsl(0.75, 0.8, 0.6))
            .f(1)
            #.fssw(-1, 1, 6)
            .t(0, 80)
            #.blendmode(BlendMode.Cycle(13))
            .chain(shake(8, 2, seed=f.i//2))
            .chain(phototype(f.a.r, 3, 90, fill=hsl(0.75, 0.8, 0.8)))
            .blendmode(BlendMode.Cycle(20))
            .chain(filmjitter(f.e("l", 4, cyclic=0), 3))
            ))
