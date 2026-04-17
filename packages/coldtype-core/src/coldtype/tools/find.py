from coldtype import *
from coldtype.tool import parse_inputs

args = parse_inputs(__inputs__, dict(
    fontSearch=[None, str, "Must provide search string"],
    fontSize=[64, int]))

fontSearch = args["fontSearch"]

results = Font.List(fontSearch, expand=True)
paths = set([r.path for r in results])

try:
    library_results = Font.LibraryList(fontSearch, expand=True)
    for l in library_results:
        if l.path not in paths:
            results.append(l)
except:
    pass


print("\nRESULTS:")
for result in results:
    print("  ", result.path)

def build_preview(x):
    #print(x.el.names())
    return (StSt(x.el.names()[0], x.el, args["fontSize"]))

previews = P().enumerate(results, build_preview)

w = max([p.ambit().w for p in previews])
h = sum([p.ambit().h for p in previews])

rect = Rect(w+20, h + 20*(len(results)+1))

@ui(rect, bg=0)
def wt1(u):
    out = previews.copy().stack(20).f(0).xalign(u.r).align(u.r).f(1)
    #for o in out:
    #    print(o)
    return P(out)

#def build(_):
#    from coldtype.osutil import show_in_finder
#    show_in_finder(fnt.path)
