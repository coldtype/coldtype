from pprint import pformat
from textwrap import indent

from coldtype import *
from coldtype.osutil import show_in_finder
from coldtype.tool import Tool, fmt_path, open_in_font_goggles

tool = Tool(ººinputsºº, dict(
    font=[None, str, "Must provide search string", "Font search string, format is optional regex for directory, then optional /, then required regex for font name (supply . for wildcard)"],
    #cond=["True", str, None, "Optional conditional python fragment for filtering; `font:Font` is passed as argument"],
    lookup=[None, str, None, "Optional conditional python fragment to print for each matching result; `font:Font` is passed as argument"],
    dst=["~/Desktop", str, None, "Optional destination when copying fonts via build command"],
    )
    , name="Find (fonts)"
    , print_fonts=False)

fonts = tool.state.get("fonts", [])

for idx, font in enumerate(fonts):
    print("")
    print(f"[{idx:3d}] {font.family}")
    #print(f"         {font.manufacturer}")
    print(f"       {font.fmtpath}")
    if lookup := tool.state.get("lookup"):
        rep = pformat(eval(lookup))
        indented = "\n".join(" " * 8 + line for line in rep.splitlines())
        print(indented)
        #_looked_up = eval(lookup)
        #if len(str(_looked_up)) > 30:
        #    pprint(_looked_up)
        #    print("---")
        #else:
        #    print("         :", eval(_looked_up))

print("\nFont Matches:", len(fonts))

if len(fonts) > 0:
    matches = fonts[:50]
    def build_preview(x):
        return (P(
            StSt(str(x.i), Font.JBMono(), 30, wght=1)
                .t(0, 8),
            StSt(x.el.family, x.el, tool.state["fontSize"])
                .t(60, 0),
            P().rect(Rect(50, 2)))
            .data(font=x.el))

    previews = P().enumerate(matches, build_preview)

    w = max([p.ambit().w for p in previews])
    h = sum([p.ambit().h for p in previews])

    rect = Rect(w+20, h + 20*(len(matches)+1))

    @renderable(rect, bg=0)
    def show_results(r):
        return (previews
            .copy()
            .stack(20)
            .align(r)
            .f(1))
    
    def build(_):
        for font in matches:
            print(f"  > Duplicated: {font.copy_to(tool.state['dst'], return_dst=True)}")
    
    numpad = { 1: partial(open_in_font_goggles, matches) }
    
    def on_click(p):
        for m in (show_results.last_return.find(lambda x: x.data("font") and p.inside(x.ambit()))):
            show_in_finder(m.data("font").path)
            #open_in_font_goggles([m.data("font")])
else:
    @renderable(540, bg=0)
    def no_results(r):
        return (StSt("NO\nRESULTS", Font.JBMono(), 72, wdth=1, wght=1)
            .align(r)
            .f("hotpink"))
