from coldtype import *
from coldtype.fx.skia import draw_canvas

from skia import textlayout, ColorBLACK, Paint, Unicodes, FontMgr, FontStyle, ColorBLUE

# adaptation of https://github.com/HinTak/skia-python-examples/blob/main/skparagraph-example.py

@animation((1080, 540), bg=1, tl=Timeline(30, 30))
def paragraph(f):
    def draw(r, canvas):
        font_collection = textlayout.FontCollection()
        font_collection.setDefaultFontManager(FontMgr())

        strut_style = textlayout.StrutStyle()
        strut_style.setStrutEnabled(True)
        #strut_style.setLeading(f.e("eeio", rng=(3.05, 0.75)))

        strut_style.setLeading(0)

        para_style = textlayout.ParagraphStyle()
        para_style.setStrutStyle(strut_style)

        builder = textlayout.ParagraphBuilder.make(para_style, font_collection, Unicodes.ICU.Make())

        paint = Paint()
        paint.setAntiAlias(True)
        paint.setColor(ColorBLACK)

        style = textlayout.TextStyle()
        style.setFontSize(30.0)
        style.setForegroundPaint(paint)
        style.setFontFamilies(["hex franklin v0.3 narrow", "times", "georgia", "serif"])
        builder.pushStyle(style)

        style_bold = style.cloneForPlaceholder()
        style_bold.setFontStyle(FontStyle.Bold())
        builder.pushStyle(style_bold)
        builder.addText("Typography")
        builder.pop()

        builder.addText(" is the ")

        style_italic = style.cloneForPlaceholder()
        style_italic.setFontStyle(FontStyle.Italic())
        #style_italic.setLetterSpacing(-2.0)
        style_italic.setWordSpacing(-10)
        paint.setColor(ColorBLUE)
        style_italic.setForegroundPaint(paint)
        builder.pushStyle(style_italic)
        builder.addText("art and technique")
        builder.pop()

        builder.addText(" of arranging type to make written language ")

        style_underline = style.cloneForPlaceholder()
        style_underline.setDecoration(textlayout.TextDecoration.kUnderline)
        style_underline.setDecorationMode(textlayout.TextDecorationMode.kGaps)
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

        paragraph.paint(canvas, r.w/2 - width/2, r.h/2 - height/2)
    
    return draw_canvas(f.a.r, draw)