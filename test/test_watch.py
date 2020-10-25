from coldtype import *


obvs_ufo = DefconFont("assets/ColdtypeObviously_BlackItalic.ufo")
generic_txt = WatchablePath("test/test_watch_scratch.txt")


@renderable(watch=[obvs_ufo.path])
def test_watch_ufo_source(r):
    return DATPen().glyph(obvs_ufo["L"]).align(r).f("hr", 0.5, 0.5)