from coldtype import *
from coldtype.blender import BlenderTimeline, b3d_sequencer

# sound: https://accent.gmu.edu/browse_language.php?function=detail&speakerid=79
# typed with: https://westonruter.github.io/ipa-chart/keyboard/

"""
pʰliz kalˠ stɛlɘ
æsk hɚ ɾɘ bɹɪŋ ðiːz θɪŋɡz wɪð hɚ fɹɔm nɘ stɔɘ
sɪks spuːnz ʌv fɹɛʃ snoʊ pʰiːz
faɪv tɪk slæbz ʌv blu tʃiːz
n meɪbi ɘ snæk fɔɹ hɚ bɹʌðɘ bɔɘb
"""

bt = BlenderTimeline(ººBLENDERºº, 275)

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=hsl(0.5)
, live_preview_scale=0.25
, audio=ººsiblingºº("media/pleasecallstella.wav")
)
def lyrics(f:Frame):
    return (f.t.words.currentWord()
        .pens(f.i, lambda c:
            (c.text, Style("Brill Italic", 350, tu=30)))
        .removeFutures()
        .align(f.a.r)
        .f(1)
        .insert(0, lambda p:
            P(p.ambit().inset(-20).drop(40, "N")).f(0)))