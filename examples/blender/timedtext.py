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
words = bt.interpretWords(include="+1 +2 +3")

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=0
, live_preview_scale=0.25
)
def timedtext(f:Frame):
    def styler(c:ClipGroupTextSetter):
        font, fs = "PolymathV", 100
        
        ital = c.styles.ki("italic").e("seo", 0)
        blue = c.styles.ki("blue")
        wght = Easeable(c.clip, f.i).e("sei", 0, rng=(0, 1))

        return (c.text, Style(font, fs
            , wght=wght
            , ital=ital
            , fill=hsl(0.6) if blue else hsl(c.i*0.05)))

    return (P(
        words.currentGroup(f.i)
            .pens(f.i, styler)
            .lead(10)
            .xalign(f.a.r, "W", tx=0)
            .align(f.a.r, tx=0)
            .remove_futures()))