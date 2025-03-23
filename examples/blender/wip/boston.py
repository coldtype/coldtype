from coldtype import *
from coldtype.blender import *
from coldtype.timing.sequence import ClipGroupTextSetter

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

ipa = bt.interpretWords(include="+1 +5 +6")
english = bt.interpretWords(include="+2")


@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=hsl(0.6, 0.7, 0.2)
, live_preview_scale=0.25
, audio=ººsiblingºº("../media/pleasecallstella.wav")
)
def lyrics(f:Frame):
    def ipa_styler(c:ClipGroupTextSetter):
        font, fs = "Brill Roman", 200
        
        if c.styles.ki("accent"):
            font, fs = "Brill Italic", 400
        if c.styles.ki("emphasis"):
            font = "Brill Bold Italic"
        
        return (c.text, Style(font, fs))

    return (P(
        english.currentGroup(f.i)
            .pens(f.i, lambda c:
                (c.text, Style("PolymathV", 60, wght=0.35, opsz=0)))
            .lead(10)
            .xalign(f.a.r)
            .align(f.a.r.take(0.35, "S"))
            .remove_futures()
            .f(1),
        ipa.currentWord(f.i)
            .pens(f.i, ipa_styler, styles=ipa.styles)
            .lead(40)
            .xalign(f.a.r)
            .align(f.a.r.take(0.85, "N"))
            .remove_futures()
            .f(1)))