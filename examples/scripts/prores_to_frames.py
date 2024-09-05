import cv2
from coldtype import *
from coldtype.img.skiaimage import SkiaImage

mov_path = Path(ººinputsºº[0]).expanduser()

print(mov_path.exists())

vc = cv2.VideoCapture(mov_path)
r = Rect(int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
frame_count = int(vc.get(cv2.CAP_PROP_FRAME_COUNT)) - 1

frames_dir = (mov_path.parent / f"{mov_path.name}__frames")
frames_dir.mkdir(exist_ok=True, parents=True)

print(frame_count)

@animation(r, tl=Timeline(frame_count))
def prores(f):
    vc.set(cv2.CAP_PROP_POS_FRAMES, f.i)
    _, frame = vc.read()
    cv2.imwrite(frames_dir / "{:05d}.jpg".format(f.i), frame)
    return P(SkiaImage(frames_dir / "{:05d}.jpg".format(f.i)), StSt(str(f.i), Font.JetBrainsMono(), 100).f(0).align(f.a.r, tx=0))