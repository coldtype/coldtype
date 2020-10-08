from pathlib import Path
from defcon import Font as DefconFont
from coldtype.text.reader import normalize_font_path, StyledString
from coldtype.pens.datpen import DATPenSet
from coldtype.interpolation import norm, interp_dict


def loopidx(lst, idx):
    return lst[idx % len(lst)]

def sibling(root, file):
    return Path(root).parent.joinpath(file)

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))

def show_points(pen, style):
    pt_labels = DATPenSet()
    def labeller(idx, x, y):
        pt_labels.append(StyledString(str(idx), style).pen().translate(x, y))
    pen.map_points(labeller)
    return pt_labels