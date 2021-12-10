from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer
from coldtype.fx.skia import phototype
from coldtype.pens.datpen import DATPensEnumerable

# sound: https://accent.gmu.edu/browse_language.php?function=detail&speakerid=79
# typed with: https://westonruter.github.io/ipa-chart/keyboard/

"""
pʰliz kalˠ stɛlɘ
æsk hɚ ɾɘ bɹɪŋ ðiːz θɪŋɡz wɪð hɚ fɹɔm nɘ stɔɘ
sɪks spuːnz ʌv fɹɛʃ snoʊ pʰiːz
faɪv tɪk slæbz ʌv blu tʃiːz
n meɪbi ɘ snæk fɔɹ hɚ bɹʌðɘ bɔɘb
"""

bt = BlenderTimeline(__BLENDER__, 250)

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=hsl(0.7)
, render_bg=1
, live_preview_scale=0.25
, audio=__sibling__("media/pleasecallstella.wav")
)
def lyrics(f:Frame):
    return (f.t.words.currentWord()
        .pens(f.i, lambda c:
            (c.text, Style("Brill Italic", 350, tu=30)))
        .removeFutures()
        .align(f.a.r)
        .f(1)
        #.print(lambda p: p[0]._frame)
        .insert(0, lambda p:
            P(p.ambit()).fssw(-1, 0, 10)))