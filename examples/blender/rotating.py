from coldtype import *
from coldtype.blender import *
from coldtype.timing.easing import all_eases
from coldtype.raster import phototype, SkiaImage


@b3d_runnable(playback=B3DPlayback.KeepPlaying)
def setup(bw:BpyWorld):
    (bw.delete_previous()
        .cycles(32, denoiser=False, canvas=Rect(1080/4), transparent=True))


@b3d_animation(Rect(1080), timeline=120, denoise=0, bg=1, upright=1, render_bg=0, solo=0)
def varfont(f):
    return (StSt("e", "Polymode_R.*V", 1200
        , RLNS=1
        , wght=f.e("seio", 1)
        , opsz=1)
        .align(f.a.r, ty=1)
        .f(0)
        .mapv(lambda p: p
            .ch(b3d(lambda bp: bp
                .extrude(0.5)
                .rotate(z=f.e("l", 0, rng=(0, -360)))))))


r = Rect(1080)
s = Scaffold(r.inset(20)).numeric_grid(11, gap=4, annotate_rings=True)

@animation(r, tl=120, bg=hsl(0.7, 0.7, 0.40), solo=1)
def manye_live(f):
    def img(x):
        #ring_e*360+f.adj(-ring*8).e(easer, 0, r=(0, -360)))
        ring = x.el.data("ring")
        #ring_e = x.el.data("ring_e")
        #easer = all_eases[ring]
        fi = f.adj(-ring*4).e("l", 0, r=(0, 120))
        return (SkiaImage(varfont.pass_path(ring*-4+round(fi)))
            .resize(0.73)
            .align(x.el.r, tx=1, ty=1))

    return (P().enumerate(s.cells(), img)
        .ch(phototype(f.a.r, 0.75, 190, 30, fill=hsl(0.7, 0.7, 0.80)))
        )