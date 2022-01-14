import os
from shutil import rmtree
from coldtype import *

if False:
    r = Rect(1000, 300)
    DP().oval(Rect(200, 200)).align(r).f(hsl(0.9)).picklejar(r)

    r = Rect(500, 300)
    DP().oval(Rect(200, 200)).align(r).f(hsl(0.3)).picklejar(r)

picklejar = Path("~/.coldtype/picklejar/").expanduser()
if picklejar.exists():
    pickles = list(picklejar.glob("*.pickle"))
    pickles.sort(key=os.path.getmtime)
else:
    picklejar.mkdir(parents=True)
    picklejar = None
    pickles = []

results = []
for pickle in pickles:
    try:
        results.append([
            pickle,
            P().Unpickle(pickle)])
    except EOFError:
        print("invalid pickle")

def make_renderable(name, result):
    r = result.data("rect", Rect(1000, 1000))
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
    except Exception as e:
        import traceback
        stack = traceback.format_exc()
        print(stack)
        print("> failed to load", pickle.stem)

#if picklejar and picklejar.exists():
#    rmtree(picklejar)

def release(_):
    for pickle, _ in results:
        try:
            pickle.unlink()
        except FileNotFoundError:
            print("> skip", pickle)