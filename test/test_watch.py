from coldtype import *

obvs_ufo = raw_ufo("assets/ColdtypeObviously_BlackItalic.ufo")
generic_txt = __sibling__("test_watch_scratch.txt")

@renderable(watch=[obvs_ufo.path, generic_txt])
def test_watch_ufo_source(r):
    return DATPens([
        DATPen().glyph(obvs_ufo["L"]).align(r).f("hr", 0.5, 0.5),
        (StyledString("> " + generic_txt.read_text() + " <",
            Style("assets/RecMono-CasualItalic.ttf", 50))
            .pens()
            .f(0.25)
            .align(r.take(150, "mny")))])