from coldtype import *
from coldtype.tool import parse_inputs
from coldtype.img.skiaimage import SkiaImage
from coldtype.renderable.animation import raw_gifski

if __as_config__:
    raise ColdtypeCeaseConfigException()

args = parse_inputs(__inputs__, dict(
    path=[None, str, "Must provide path to frames"],
    fps=[18, float],
    output_folder=[".", str],
    ))

template = args["path"] + "{:04d}.png"

img0_path = ººsiblingºº(template.format(0))
img0 = SkiaImage(img0_path)

name = (img0_path.parent.parent.stem + "_" + img0_path.stem).replace("_0000", "")
count = len(list(img0_path.parent.glob("*.png")))

output_folder = Path(args["output_folder"])
output_folder.mkdir(exist_ok=True, parents=True)

#print(args)
print(">", name)

@animation(img0.rect(), tl=Timeline(count, fps=args["fps"]), name=name)
def gifmaker(f):
    return (SkiaImage(ººsiblingºº(template.format(f.i))))

@renderable(Rect(img0.rect().w, 70), bg=None)
def instructions(r):
    return (StSt(str(args["fps"]) + " fps / [r] (release) for gif", Font.JBMono(), 32, wght=1)
        .align(r)
        .f(0))

def release(_):
    raw_frames = []
    for fi in range(gifmaker.timeline.start, gifmaker.timeline.end):
        raw_frames.append(template.format(fi))
        if not Path(raw_frames[-1]).exists():
            raise Exception("frame does not exist", raw_frames[-1])
    
    raw_gifski(gifmaker.rect.w, gifmaker.timeline.fps, raw_frames, output_folder / (name + ".gif"), open=True)