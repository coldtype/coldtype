import exrex

from coldtype import *
from coldtype.tool import Tool
from coldtype.osutil import show_in_finder


tool = Tool(ººinputsºº, dict(
    font=[Font.RecursiveMono(), str, None, "Font search string"],
    scale=[1.25, float, None, "Scale for window (chars will size up to fill)"],
    variations=["{}", str, None, "Variations, as eval-able python string"],
    subset=[None, str, None, "Subset the font to only characters represented by this regex; hitting 2 in viewer will run pyftsubset with these characters"],
    dst=["~/Desktop", str, None, "Folder where subsetted fonts should appear"]
    )
    , ui=ººuiºº
    , name="Character Set Display"
    , doc="• Click something to see information printed in the terminal\n• Hit 1 in viewer to reveal current font in finder")


scale = tool.state["scale"]
r = Rect(1080*scale, 1080*scale + (h:=120))


if subset := tool.state["subset"]:
    subset = list(exrex.generate(subset))

fonts = tool.state["fonts"]

fnt:Font = fonts[0]
gsub = fnt.font.ttFont["GSUB"].table

stylistic_sets = {}

for fr in gsub.FeatureList.FeatureRecord:
    if not fr.FeatureTag.startswith("ss"):
        continue

    stylistic_sets[fr.FeatureTag] = {}
    
    feature = fr.Feature
    for lookup_idx in feature.LookupListIndex:
        lookup = gsub.LookupList.Lookup[lookup_idx]
        for subtable in lookup.SubTable:
            # LookupType 1 = Single Substitution
            if lookup.LookupType == 1:
                for glyph, sub in subtable.mapping.items():
                    stylistic_sets[fr.FeatureTag][glyph] = sub
            # LookupType 3 = Alternate Substitution (multiple alternates per glyph)
            elif lookup.LookupType == 3:
                for glyph, alt_set in subtable.alternates.items():
                    stylistic_sets[fr.FeatureTag][glyph] = alt_set


sq = math.ceil(math.sqrt(max([len(s.values()) for s in stylistic_sets.values()])))


@animation(r, bg=1, tl=Timeline(len(stylistic_sets)))
def chars_display(f):
    set_name = list(stylistic_sets.keys())[f.i]

    sset = stylistic_sets[set_name]
    glyphs = sset.values()
    #sq = math.ceil(math.sqrt(len(glyphs)))

    glyphSet = fnt.font.ttFont.getGlyphSet(location={"wght":750,"wdth":110})

    r = f.a.r.drop(h, "N")
    grid = r.grid(sq, sq)

    return (P()
        .enumerate(glyphs, lambda x: P().glyph(glyphSet[x.el], glyphSet).scale(1/sq).f(0).align(grid[x.i]))
        .append(P().gridlines(r, sq, sq))
        .append(P(
            P(r:=f.a.r.take(h, "N")).f(0),
            StSt(fnt.family, Font.JBMono(), 30, wght=0.5).align(r.inset(25), "NW").f(1),
            StSt(f"{set_name} — {fnt.font.stylisticSetNames[set_name]}", Font.JBMono(), 32, wght=1).align(r.inset(25), "SW").f(1))))


numpad = {
    1: lambda _: show_in_finder(fnt.path),
    2: lambda _: fnt.subset((Path(tool.state["dst"]) / (fnt.path.stem + "_subset" + fnt.path.suffix)).expanduser(), text="".join(subset))
}


def on_click(pos):
    for m in (chars_display.last_return
        .find(lambda x: x.data("char") and pos.inside(x.ambit()))):
        char = m.data("char")
        print(f"> {char} \\u{ord(char):04X} {m.data('gn')}")