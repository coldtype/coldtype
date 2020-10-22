from coldtype.test import *

@test()
def space_as_glyph(r):
    glyphs = (StyledString("A B",
        Style(mutator, 500, include_blanks=1))
        .pens()
        .align(r))
    
    return (glyphs
        + glyphs.frameSet().s(0, 0.25).sw(15))