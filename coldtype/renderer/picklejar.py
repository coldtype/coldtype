import os
from coldtype import *

if False:
    r = Rect(1000, 300)
    DP().oval(Rect(200, 200)).align(r).f(hsl(0.9)).picklejar(r)

    r = Rect(500, 300)
    DP().oval(Rect(200, 200)).align(r).f(hsl(0.3)).picklejar(r)

picklejar = Path("~/.coldtype/picklejar").expanduser()
if picklejar.exists():
    pickles = list(picklejar.glob("*.pickle"))
    pickles.sort(key=os.path.getmtime)
else:
    picklejar = None
    pickles = []

results = []
for pickle in pickles:
    results.append([
        pickle,
        DP().Unpickle(pickle)])

def make_renderable(name, result):
    r = result.data.get("rect", Rect(1000, 1000))
    @renderable(r)
    def pj(r): # TODO naming needs to be different?
        return result
    pj.name = name
    return pj

RENDERABLES = []
for result in results:
    pickle, res = result
    try:
        RENDERABLES.append(make_renderable(pickle.stem, res))
    except:
        print("failed to load", pickle.stem)

for pickle, _ in results:
    pickle.unlink()