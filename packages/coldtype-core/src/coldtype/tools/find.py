from coldtype import *
from coldtype.tool import parse_inputs

args = parse_inputs(__inputs__, dict(
    fontSearch=[None, str, "Must provide search string"],
    fontSize=[64, int],
    dst=["~/Desktop", str]))

results = Font.ListAll(args["fontSearch"])
results = results[:30]

def fmt_path(path: Path) -> str:
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)

if len(results) > 0:
    maxsys = max([len(f.system_name) for f in results])
    maxpat = max([len(fmt_path(f.path)) for f in results])
    print("\n")
    print(f"    # {'Name':<{maxsys}} Path")
    print(f"  {'-'*(maxsys+maxpat+3)}")
    for idx, result in enumerate(results):
        print(f"  {idx:>{3}} {result.system_name:<{maxsys}} {fmt_path(result.path)}")
    print("\n")

    def build_preview(x):
        return (P(
            StSt(str(x.i), Font.JBMono(), 30, wght=1)
                .t(0, 8),
            StSt(x.el.names()[0], x.el, args["fontSize"])
                .t(60, 0),
            P().rect(Rect(50, 2)))
            .data(font=x.el))

    previews = P().enumerate(results, build_preview)

    w = max([p.ambit().w for p in previews])
    h = sum([p.ambit().h for p in previews])

    rect = Rect(w+20, h + 20*(len(results)+1))

    @renderable(rect, bg=0)
    def show_results(r):
        return (previews
            .copy()
            .stack(20)
            #.xalign(r)
            .align(r)
            .f(1))
    
    def build(_):
        for font in results:
            print(f"  > Duplicated: {font.copy_to(args['dst'], return_dst=True)}")
        
else:
    @renderable(540, bg=0)
    def no_results(r):
        return (StSt("NO\nRESULTS", Font.JBMono(), 72, wdth=1, wght=1)
            .align(r)
            .f("hotpink"))

#def build(_):
#    from coldtype.osutil import show_in_finder
#    show_in_finder(fnt.path)