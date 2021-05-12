from coldtype.pens.datpen import DATPen
import drafting.text.reader
from coldtype.pens.datpen import DATPen, DATPens

drafting.text.reader._PenClass = DATPen
drafting.text.reader._PensClass = DATPens

import drafting.text.composer

from drafting.geometry.rect import Rect
from drafting.text.reader import Style, StyledString, SegmentedString, normalize_font_path, Font, FontNotFoundException
from drafting.text.composer import Slug, Lockup, Graf, GrafStyle, T2L, Composer, StSt
#from coldtype.text.richtext import RichText