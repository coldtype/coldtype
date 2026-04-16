from coldtype import *
from coldtype.tool import parse_inputs

# TODO single-frame animated version?

args = parse_inputs(__inputs__, dict(
    font=[None, str, "Must provide font regex or path"],
    fontSize=[72, int]))

fnt = args["font"]
font = fnt.font.ttFont
cmap = fnt.font.ttFont["cmap"]
best = cmap.getBestCmap()

#for table in font["cmap"].tables:
#    print(f"Platform {table.platformID}, Encoding {table.platEncID}, Format {table.format}")

els = []

if best:
    all_chars = []
    cmap = fnt.font.ttFont["cmap"]
    for ch, name in cmap.getBestCmap().items():
        all_chars.append(chr(ch))
    els = all_chars
else:
    symbol_cmap = font["cmap"].getcmap(3, 0)

    # if symbol_cmap:
    #     for codepoint, glyph_name in symbol_cmap.cmap.items():
    #         typeable_char = chr(codepoint & 0xFF)  # strip the 0xF0 prefix
    #         print(f"Type '{typeable_char}' (0x{codepoint:04X}) -> {glyph_name}")

    if symbol_cmap:
        all_chars = []
        for codepoint, glyph_name in symbol_cmap.cmap.items():
            low_byte = codepoint & 0xFF
            char = chr(low_byte)
            if char.isprintable() and low_byte >= 0x20:
                display = f"'{char}'"
                all_chars.append(char)
            else:
                display = f"\"\\u{low_byte:04X}\""
                all_chars.append(f"\\u{low_byte:04X}")
        els = all_chars

sq = math.ceil(math.sqrt(len(els)))
fs = args["fontSize"]

def getGlyph(x):
    txt = x.el
    if txt.startswith("\\u"): txt = txt.encode().decode('unicode_escape')
    return StSt(txt, fnt, fs).pen()

glyphs = P().enumerate(els, getGlyph)

maxr:Rect = max([g.ambit(tx=1, ty=1) for g in glyphs])
maxr = maxr.square(outside=True).round().inset(-5).zero()

sq = math.ceil(math.sqrt(len(els)))
rect = Rect(sq*maxr.w, sq*maxr.w)

@ui(rect, bg=1)
def wt1(u):
    rs = u.r.inset(10).grid(sq, sq)
    
    def showChar(x):
        if u.c.inside(rs[x.i]): print(">", x.el)
        return (P(glyphs[x.i].copy().f(0).align(rs[x.i])))

    return P(
        P().gridlines(u.r.inset(10), sq, sq),
        P().enumerate(els, showChar))

def build(_):
    from coldtype.osutil import show_in_finder
    show_in_finder(fnt.path)

# @ui(args["rect"], bg=1)
# def wt1(u):
#     rs = u.r.inset(10).grid(sq, sq)
    
#     def showChar(x):
#         if u.c.inside(rs[x.i]):
#             print(">", x.el)

#         if by_char:
#             txt = x.el
#             if txt.startswith("\\u"):
#                 txt = txt.encode().decode('unicode_escape')
            
#             return P(StSt(txt, fnt, fs)
#                     .align(rs[x.i])
#                     .f(0),
#                 P().text(x.el,
#                     Style("Times", 24
#                         , load_font=0
#                         , fill=hsl(0.8))
#                     , rs[x.i].inset(5)) if args["chars"] else None)
#         else:
#             glyph = glyphSet[x.el]
#             return (P()
#                 .glyph(glyph, glyphSet).f(0).scale(fs/750, pt=(0, 0))
#                 .align(rs[x.i])
#                 .scaleToRect(rs[x.i].inset(6), shrink_only=1, preserveAspect=1))

#     return P(
#         P().gridlines(u.r.inset(10), sq, sq),
#         P().enumerate(els, showChar))