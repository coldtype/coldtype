from coldtype import *
from coldtype.renderable.animation import skia_direct_animation

from skia import textlayout, ColorBLACK, Paint, Unicodes, FontMgr, FontStyle, ColorWHITE

# adaptation of https://github.com/HinTak/skia-python-examples/blob/main/skparagraph-example.py

@skia_direct_animation((1080, 540), tl=30)
def paragraph(f, canvas):
    r = f.a.r

    font_collection = textlayout.FontCollection()
    font_collection.setDefaultFontManager(FontMgr())

    para_style = textlayout.ParagraphStyle()
    # SK_DISABLE_LEGACY_PARAGRAPH_UNICODE: two-arg ParagraphBuilder constructor used by rust going soon!
    builder = textlayout.ParagraphBuilder.make(para_style, font_collection, Unicodes.ICU.Make())

    paint = Paint()
    paint.setAntiAlias(True)
    paint.setColor(ColorBLACK)

    style = textlayout.TextStyle()
    style.setFontSize(30.0)
    style.setForegroundPaint(paint)
    style.setFontFamilies(["times", "georgia", "serif"])
    builder.pushStyle(style)

    style_bold = style.cloneForPlaceholder()
    style_bold.setFontStyle(FontStyle.Bold())
    builder.pushStyle(style_bold)
    builder.addText("Typography")
    builder.pop()

    builder.addText(" is the ")

    style_italic = style.cloneForPlaceholder()
    style_italic.setFontStyle(FontStyle.Italic())
    builder.pushStyle(style_italic)
    builder.addText("art and technique")
    builder.pop()

    builder.addText(" of arranging type to make written language ")

    style_underline = style.cloneForPlaceholder()
    style_underline.setDecoration(textlayout.TextDecoration.kUnderline)
    style_underline.setDecorationMode(textlayout.TextDecorationMode.kGaps) # Rust seems to default to kGaps, while kThrough is the upstream default.
    style_underline.setDecorationColor(ColorBLACK)
    style_underline.setDecorationThicknessMultiplier(1.5)
    builder.pushStyle(style_underline)
    builder.addText("legible, readable, and appealing")
    builder.pop()

    builder.addText(" when displayed. The arrangement of type involves selecting typefaces, point sizes, line lengths, line-spacing (leading), and letter-spacing (tracking), and adjusting the space between pairs of letters (kerning). The term typography is also applied to the style, arrangement, and appearance of the letters, numbers, and symbols created by the process.")

    builder.addText(" Furthermore, العربية نص جميل. द क्विक ब्राउन फ़ॉक्स jumps over the lazy 🐕.")

    ri = r.inset(f.e("eeio", rng=(10, 300)))

    paragraph = builder.Build()
    paragraph.layout(ri.w)

    width = paragraph.LongestLine
    height = paragraph.Height

    #canvas = surface.getCanvas()
    canvas.clear(ColorWHITE)
    paragraph.paint(canvas, r.w/2 - width/2, r.h/2 - height/2) # What does rust's Point() do?