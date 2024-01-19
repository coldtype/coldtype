from coldtype import *

def value_as_skia_path_commands(self):
    for mv, pts in self.v.value:
        method = ({"closePath":"close"}).get(mv, mv)
        flat_pts = [round(item) for row in pts for item in row]
        pts_string = ",".join([str(p) for p in flat_pts])
        print(f"path.{method}({pts_string})")

@renderable(rect=(1200, 340), bg=0)
def render(r):
    return (StSt("T", Font.MuSan(), 200)
        .align(r)
        .pen()
        .removeOverlap()
        #.print(lambda p: value_as_skia_path_commands(p))
        .f(1))