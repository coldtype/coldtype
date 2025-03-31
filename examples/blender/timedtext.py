from coldtype import *
from coldtype.blender import *
from coldtype.timing.sequence import ClipGroupTextSetter

# Blender
#   - Switch to "Video Editing"
#   - View "Tool" in Sequencer
#   - CT2D: Hit "Settings > Defaults"
#   - Author data
#   - CT2D: Import > Preview
#   - Create Image Editor, select image live preview
#   - CT2D: Render > Film reel (render all)
#   - CT2D: Import > Frames

# Gotchas
# Only set timeline length and fps in Coldtype code
#   (not in Blender itself)

bt = BlenderTimeline(ººBLENDERºº, 130, 30)
words = bt.interpretWords(include="+1 +2 +3")

@b3d_sequencer((1080, 1080)
, timeline=bt
, bg=0
, live_preview_scale=0.25
)
def timedtext(f:Frame):
    def styler(c:ClipGroupTextSetter):
        font, fs = "PolymathV", 100
        
        blue = c.styles.ki("blue")
        ital = c.styles.ki("italic").e("seo", 0)
        wght = 1 if c.styles.ki("static") else Easeable(c.clip, f.i).e("sei", 0, rng=(0, 1))

        return (c.text, Style(font, fs
            , wght=wght
            , ital=ital
            , fill=hsl(0.6) if blue else hsl(c.clip.idx*0.025)))

    return (P(
        words.currentGroup(f.i)
            .pens(f.i, styler)
            .lead(10)
            .xalign(f.a.r, "W", tx=0)
            .align(f.a.r, tx=0)
            .remove_futures()))