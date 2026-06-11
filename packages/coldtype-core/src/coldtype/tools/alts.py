import exrex

from coldtype import *
from coldtype.tool import Tool
from coldtype.osutil import show_in_finder


tool = Tool(ººinputsºº, dict(
    font=[Font.RecursiveMono(), str, None, "Font search string"],
    scale=[1.25, float, None, "Scale for window (chars will size up to fill)"],
    dst=["~/Desktop", str, None, "Folder where subsetted fonts should appear"]
    )
    , ui=ººuiºº
    , name="Character Set Display"
    , doc="• Click something to see information printed in the terminal\n• Hit 1 in viewer to reveal current font in finder")


scale = tool.state["scale"]
r = Rect(1080*scale, 1080*scale + (h:=120))

fonts = tool.state["fonts"]

fnt:Font = fonts[0]
gsub = fnt.font.ttFont["GSUB"].table

style = Style(fnt, 24, variations=tool.state["fontVariations"])
#print(style.variations, tool.state["fontVariations"])

substitutions = {}

for fr in gsub.FeatureList.FeatureRecord:
    if fr.FeatureTag.startswith("ss") or fr.FeatureTag.startswith("cv") or fr.FeatureTag.startswith("aa"):
        substitutions[fr.FeatureTag] = {}
        
        feature = fr.Feature
        for lookup_idx in feature.LookupListIndex:
            lookup = gsub.LookupList.Lookup[lookup_idx]
            for subtable in lookup.SubTable:
                # LookupType 1 = Single Substitution
                if lookup.LookupType == 1:
                    for glyph, sub in subtable.mapping.items():
                        substitutions[fr.FeatureTag][glyph] = sub
                # LookupType 3 = Alternate Substitution (multiple alternates per glyph)
                elif lookup.LookupType == 3:
                    for glyph, alt_set in subtable.alternates.items():
                        substitutions[fr.FeatureTag][glyph] = alt_set


print(substitutions.keys())

sq = 1

def build_view(glyphs):
    view = P()
    glyphSet = fnt.font.ttFont.getGlyphSet(location=style.variations)

    for g in glyphs:
        try:
            view.append(P().glyph(glyphSet[g], glyphSet).f(0))
        except Exception as e:
            #print(e)
            pass
    
    return view

def align_view(view, grid, _sq):
    return view.mapv(lambda idx, p: p.scale(1/_sq).align(grid[idx]))

max_glyphs = max([len(s.values()) for s in substitutions.values()])

if "aalt" in substitutions and True:
    aalt = build_view(substitutions["aalt"].values())
    max_glyphs = len(aalt)

sq = math.ceil(math.sqrt(max_glyphs))


@animation(r, bg=1, tl=Timeline(len(substitutions)))
def chars_display(f):
    set_name = list(substitutions.keys())[f.i]

    r = f.a.r.drop(h, "N")

    view = build_view(substitutions[set_name].values())

    _sq = math.ceil(math.sqrt(len(view)))
    grid = r.grid(_sq, _sq)
    align_view(view, grid, _sq)

    return (P()
        .append(view)
        .append(P().gridlines(r, _sq, _sq))
        .append(P(
            P(r:=f.a.r.take(h, "N")).f(0),
            StSt(fnt.family, Font.JBMono(), 30, wght=0.5).align(r.inset(25), "NW").f(1),
            StSt(f"{set_name} — {fnt.font.stylisticSetNames.get(set_name, set_name)}", Font.JBMono(), 32, wght=1).align(r.inset(25), "SW").f(1))))


numpad = {
    1: lambda _: show_in_finder(fnt.path),
    #2: lambda _: fnt.subset((Path(tool.state["dst"]) / (fnt.path.stem + "_subset" + fnt.path.suffix)).expanduser(), text="".join(subset))
}


def on_click(pos):
    for m in (chars_display.last_return
        .find(lambda x: x.data("char") and pos.inside(x.ambit()))):
        char = m.data("char")
        print(f"> {char} \\u{ord(char):04X} {m.data('gn')}")