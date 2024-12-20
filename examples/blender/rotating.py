from coldtype import *
from coldtype.blender import *
from coldtype.raster import phototype

@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def setup(bw:BpyWorld):
    (bw.delete_previous()
        .cycles(32, denoiser=False, canvas=Rect(1080/4), transparent=True))

@b3d_animation(Rect(1080), timeline=120, denoise=0, bg=1, upright=1, render_bg=0
    , solo=ººBLENDERINGºº)
def varfont(f):
    return (StSt("e", Font.JBMono(), 1200
        , wght=f.e("seio", 1))
        .align(f.a.r, ty=1)
        .f(0)
        .mapv(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.5)
                .rotate(z=f.e("l", 0, rng=(0, -360)))))))

r = Rect(1080)
s = Scaffold(r.inset(10)).numeric_grid(9, gap=4, annotate_rings=True)

@animation(r, tl=120, bg=hsl(0.7, 0.7, 0.45)
    , solo=not ººBLENDERINGºº
    , release=λ.export("h264", loops=8))
def manye_live(f):
    def img(x):
        ring = x.el.data("ring")
        fi = f.adj(-ring*4).e("l", 0, r=(0, 120))
        return (varfont.pass_img(ring*-4+round(fi))
            .resize(0.77)
            .align(x.el.r, tx=1, ty=1))

    return (P().enumerate(s.cells(), img)
        .ch(phototype(f.a.r, 0.75, 180, 30, fill=hsl(0.7, 0.7, 0.85))))