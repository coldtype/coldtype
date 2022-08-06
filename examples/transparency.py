from coldtype import *

f = bw(0.9)

@renderable((d:=30, d), bg=1, render_bg=1)
def blocks(r):
    g = Grid(r, "a a", "a a", "a b / c d")
    return (P(g["a"]).f(f), P(g["d"]).f(f))

def release(passes):
    import subprocess
    subprocess.run(["ditto", passes[0].output_path, "coldtype/demo/"])
    print("ditto'd")