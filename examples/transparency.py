from coldtype import *

f = bw(0.9)

@renderable(30, bg=1, render_bg=1)
def blocks(r):
    s = Scaffold(r).numeric_grid(2, 2)
    return [P(s["0|1"]).f(f), P(s["1|0"]).f(f)]

@renderable(1024, bg=-1)
def appicon(r):
    return (StSt("C", Font.ColdObvi(), 1280)
        .align(r))

def release(_):
    from shutil import copy2
    blocks_path = blocks.render_to_disk(render_bg=1)[0]
    copy2(blocks_path, Path("src/coldtype/demo") / blocks_path.name)

    icon_path = appicon.render_to_disk(render_bg=0)[0]
    copy2(icon_path, Path("src/coldtype/demo") / icon_path.name)