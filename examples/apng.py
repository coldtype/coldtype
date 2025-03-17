from coldtype import *


def release_apng(a:animation):
    fe = FFMPEGExport(a, False, loops=1)
    fe.fmt = "png"
    fe.args = fe.args[:-4] + ["-plays", "0", "-f", "apng"]
    fe.write(verbose=True)
    fe.open()


@animation((1080, 720), tl=30, release=release_apng)
def scratch(f:Frame):
    return (StSt(".PNG", Font.MuSan(), 300, wght=f.e("eeio"))
        .align(f.a.r, ty=0)
        .f(hsl(f.e("l", 0 )))
        .rotate(f.e("eeio", 1, rng=(-20, 20))))
