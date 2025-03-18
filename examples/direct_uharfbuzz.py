from coldtype import *
import uharfbuzz as hb

file = Path(ººFILEºº).parent.parent / "src/coldtype/demo/JetBrainsMono.ttf"

blob = hb.Blob.from_file_path(file)
face = hb.Face(blob)

@renderable(bg=1)
def scratch(r:Rect):
    font = hb.Font(face)
    font.set_variations(dict(wght=800))

    buf = hb.Buffer()
    buf.add_str("xyz")
    buf.guess_segment_properties()

    features = {"kern": True, "liga": True}
    hb.shape(font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions
    advance = 0

    def glyph(x):
        nonlocal advance
        info, pos = x.el
        gid = info.codepoint
        p = P()
        font.draw_glyph_with_pen(gid, p)
        p.translate(advance + pos.x_offset, pos.y_offset)
        advance += pos.x_advance
        return p

    return (P().enumerate(zip(infos, positions), glyph)
        .scale(0.25)
        .align(r)
        .f(0))