from coldtype import *

font_zip_url = "https://github.com/aminabedi68/Estedad/releases/download/7.3/Estedad-v7.3.zip"
estedad_variable = Font.UnzipURL(font_zip_url, "Estedad-FD[KSHD,wght].ttf", "Variable")

@animation((1080, 540), bg=1, tl=30, release=λ.export("h264", loops=4))
def kashida(f:Frame):
    txt = "مرحبًا"
    rh = random_series(seed=1)
    fs = 200

    return (Glyphwise2(txt,
        lambda g: Style(estedad_variable, fs, wght=f.e("seio"), KSHD=f.adj(-g.i*10).e("seio")))
        .mapv(lambda i, p: p.f(hsl(rh[i])))
        .align(f.a.r, ty=1))
