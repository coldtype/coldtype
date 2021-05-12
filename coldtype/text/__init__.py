from coldtype.pens.datpen import DATPen
import drafting.text.reader
from coldtype.pens.datpen import DATPen, DATPens

drafting.text.reader._PenClass = DATPen
drafting.text.reader._PensClass = DATPens

import drafting.text.composer

from drafting.geometry.rect import Rect
from drafting.text.reader import Style, StyledString, SegmentedString, normalize_font_path, Font, FontNotFoundException
from drafting.text.composer import Slug, Lockup, Graf, GrafStyle, T2L, Composer
#from coldtype.text.richtext import RichText

def StSt(text,
    font,
    font_size,
    rect=Rect(1080, 1080),
    **kwargs):
    style = Style(font, font_size, **kwargs)
    fit = kwargs.get("fit", None)
    leading = kwargs.get("leading", 10)
    if "\n" in text:
        lockup = Composer(rect, text, style, fit=fit, leading=leading)
    else:
        lockup = StyledString(text, style)
    return lockup