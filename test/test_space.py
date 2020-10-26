from coldtype.test import *

@test()
def space_as_glyph(r):
    glyphs = (StyledString("A B",
        Style(mutator, 500))
        .pens()
        .align(r))
    
    return (glyphs
        + glyphs.frameSet().s(0, 0.5).sw(5))


@test()
def space_glyph_set_width(r):
    glyphs = (StyledString("A B",
        Style(mutator, 500, space=1000))
        .pens()
        .align(r))
    
    return (glyphs
        + glyphs.frameSet().s(0, 0.5).sw(5))