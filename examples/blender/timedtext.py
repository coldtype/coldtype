from coldtype import *
from coldtype.blender import *
from coldtype.timing.sequence import ClipGroupTextSetter

# Blender
#   - Switch to "Video Editing"
#   - View "Tool" in Sequencer
#   - Hit "Set Defaults"
#   - Author data
#   - Import Live Preview
#   - Create Image Editor, select image live preview
#   - Render All
#   - Import Frames

bt = BlenderTimeline(ººBLENDERºº, 120)
words = bt.interpretWords(include="+1 +2")

fonts = [
    "ObviouslyV",
    "PolymathV",
    Font.JBMono(),
    "DegularV",
    "CheeeV"
]

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=0
, live_preview_scale=0.25
)
def timedtext(f:Frame):
    return (Lockup([
        StyledString("A", Style("ObviouslyV", 100, wght=0, wdth=0)),
        StyledString("B", Style("ObviouslyV", 100, wght=1, wdth=1))]
        )
        .pens()
        .align(f.a.r))

    def styler(c:ClipGroupTextSetter):
        font, fs = Font.JBMono(), 100
        wght = c.styles.current().e("eeio", 0)

        return (c.text, Style(font, fs#+c.i*50
            , wght=wght
            , fill=hsl(c.i*0.05)))

    return (P(
        words.currentGroup(f.i)
            .pens(f.i, styler, verbose=True)
            #.lead(10)
            #.xalign(f.a.r, tx=0)
            #.align(f.a.r, tx=0)
            #.remove_futures()
            ))