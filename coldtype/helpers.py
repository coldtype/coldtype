from pathlib import Path
from defcon import Font as DefconFont
from coldtype.text.reader import normalize_font_path, StyledString
from coldtype.pens.datpen import DATPenSet
from coldtype.interpolation import norm, interp_dict
from random import Random


def loopidx(lst, idx):
    return lst[idx % len(lst)]

def sibling(root, file):
    return Path(root).parent.joinpath(file)

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))

def ßhide(el):
    return None

def ßshow(el):
    return el

def random_series(start=0, end=1, seed=0, count=5000):
    rnd = Random()
    rnd.seed(seed)
    rnds = []
    for x in range(count):
        rnds.append(start+rnd.random()*(end-start))
    return rnds

def show_points(pen, style):
    pt_labels = DATPenSet()
    def labeller(idx, x, y):
        pt_labels.append(StyledString(str(idx), style).pen().translate(x, y))
    pen.map_points(labeller)
    return pt_labels