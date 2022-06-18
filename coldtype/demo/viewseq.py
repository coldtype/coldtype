from coldtype import *
from coldtype.tool import parse_inputs
from coldtype.img.skiaimage import SkiaImage

args = parse_inputs(__inputs__, dict(
    path=[None, str, "Must provide path to image sequence"],
    fps=[30, float],
    dirsort=["x.name", str],
    ))

dirsort = eval(f"lambda x: {args['dirsort']}")

def find_pngs(_root):
    return sorted(list(_root.glob("*.png")), key=lambda p: p.stem.split("_")[-1])

root = Path(args["path"]).expanduser().absolute()
images = find_pngs(root)

if len(images) == 0:
    for dir in sorted(filter(lambda x: not x.name.startswith("."), root.iterdir()), key=dirsort):
        if not dir.name.startswith("."):
            images.extend(find_pngs(dir))

sk1 = SkiaImage(images[0])

@animation(sk1.bounds(), tl=Timeline(len(images), fps=args["fps"]))
def viewseq(f):
    ski = SkiaImage(images[f.i])
    return (P(f.a.r).img(ski, f.a.r))