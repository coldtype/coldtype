from coldtype import *
from coldtype.tool import parse_inputs
from coldtype.renderable.animation import image_sequence
from coldtype.img.skiaimage import SkiaImage

args = parse_inputs(__inputs__, dict(
    path=[None, str, "Must provide path to image sequence"],
    fps=[30, float],
    fmt=["h264", str],
    date=[False, bool],
    loops=[1, int],
    audio=[None, str],
    set709=[True, bool],
    dirsort=["x.name", str],
    ))

dirsort = eval(f"lambda x: {args['dirsort']}")

def find_pngs(_root):
    return sorted(list(_root.glob("*.png")), key=lambda p: p.stem.split("_")[-1])

root = Path(args["path"]).expanduser().absolute()

if not root.exists():
    raise Exception("viewseq root path not found")

images = find_pngs(root)

if len(images) == 0:
    for dir in sorted(filter(lambda x: not x.name.startswith("."), root.iterdir()), key=dirsort):
        if not dir.name.startswith("."):
            images.extend(find_pngs(dir))

def releaser(x:animation):
    fe = FFMPEGExport(x, date=args["date"], loops=args["loops"], audio=args["audio"], set_709=args["set709"], output_folder=root.parent)
    
    if args["fmt"] == "h264":
        fe.h264()
    elif args["fmt"] == "mov":
        fe.prores()
    elif args["fmt"] == "gif":
        fe.gif()
    
    fe.write(verbose=True, name=root.stem)
    fe.open()

@image_sequence(images, args["fps"], looping=False, release=releaser)
def viewseq(_): return None

# def release():
#     dst_dir = images[0].parent.parent.parent
#     dst_name = images[0].parent.parent.stem

#     print(dst_dir, dst_name)