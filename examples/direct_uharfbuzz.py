from coldtype import *
import uharfbuzz as hb

ct_font = Font.Find("JetBrainsMono.ttf")

blob = hb.Blob.from_file_path(ct_font.path)
face = hb.Face(blob)

@renderable(bg=1)
def direct(r:Rect):
    font = hb.Font(face)
    
    ttFont = ct_font.font.ttFont

    cap_height = ttFont['OS/2'].sCapHeight

    max_wght = ct_font.variations()["wght"]["maxValue"]
    font.set_variations(dict(wght=max_wght))

    buf = hb.Buffer()
    buf.add_str("bag")
    buf.guess_segment_properties()

    features = {"kern": True, "liga": True}
    hb.shape(font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    def glyph(x):
        info, pos = x.el
        gid = info.codepoint
        p = P()
        font.draw_glyph_with_pen(gid, p)
        p.translate(pos.x_offset, pos.y_offset)
        # set the typographical "frame" (this is a special property that .align calls check for)
        p.data(frame=Rect(pos.x_offset, pos.y_offset, pos.x_advance, cap_height))
        return p

    return (P().enumerate(zip(infos, positions), glyph)
        .spread(60) # 60 is equivalent to display-space tracking
        .scale(0.5, pt=(0,0))
        .align(r, tx=0)
        .f(0)
        .mapv(lambda p: p
            .up()
            .insert(0, P().rect(p.ambit()).fssw(-1, hsl(0.9, 0.7, 0.9), 2))))