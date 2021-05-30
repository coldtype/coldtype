from coldtype.test import *
import coldtype.filtering as fl
from coldtype.warping import warp_fn

fonts = [Font.Cacheable(f"~/Type/fonts/fonts/{f}") for f in [
    "MDNichrome0.7-Bold.otf",
    "MeekDisplayv0.2-Bold.otf"
]]

def improved(e, xo=0, yo=0, xs=1, ys=1, base=1):
    noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.015, 0.015, 3, base)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)

bases = random_series(0, 1000)
adj_x = random_series(-500, 500)
adj_y = random_series(-0.1, 0.1)

@animation((1080, 1080), bg=0, timeline=Timeline(100, fps=22), composites=1, bg_render=True)
def displacement(f):
    r = f.a.r
    spots = (DATPen()
        .f(1)
        #.oval(r.inset(300))
        .precompose(r)
        .attr(skp=dict(
            #PathEffect=skia.DiscretePathEffect.Make(5.0, 15.0, 0),
            Shader=improved(1, xo=300, yo=200, xs=0.35, ys=0.5, base=bases[f.i]/2).makeWithColorFilter(fl.compose(
                fl.fill(bw(0)),
                fl.as_filter(fl.contrast_cut(230, 1)), # heighten contrast
                skia.LumaColorFilter.Make(), # knock out
            )),
        )))
    

    spots = (DATPens([
            displacement.last_result.filmjitter(f.a.progress(f.i).e, speed=(50, 50), scale=(3, 5)) if f.i != -1 and displacement.last_result else None,
            DATPen().rect(r).f(1, 0.1),
            spots,
            #Composer(f.a.r, "Inkblot\nTest".upper(), Style(obv, 250, ro=1, slnt=1, wght=0.75, wdth=0.2+0.4*f.a.progress(f.i, easefn=["ceio"], loops=5).e)).pens().xa().pen().f(0).s(1).sw(7).align(f.a.r).translate(0, -600+f.i*10),
        ]))
    
    fi = (f.i + 9) % 100
    if fi % 1 == 0:
        ii = 10-((fi)//10)
        if ii >= 0:
            je = pow(((fi)%10), 3.1)
            spots.append(StyledString(
                str(ii),
                Style(fonts[ii%2], -10+je, ro=1))
                .pen()
                .f(1)
                .s(1)
                .sw(15)
                .align(r, th=1)
                .blendmode(skia.BlendMode.kXor))
        
    #return spots
    if f.i == 0:
        spots.insert(2, DATPen().rect(f.a.r).f(0 if f.i != 90 else hsl(0.7, l=0.3)))
    return spots.color_phototype(r.inset(0), cut=110, blur=1.5, cutw=50, rgba=[1, 1, 1, 1])
    
    spots_img = spots.attrs["default"]["image"]["src"]
    spots_img_filter = skia.ImageFilters.Image(spots_img)

    grade = DATPen().rect(r).f(Gradient.Vertical(r, hsl(0), hsl(0.5)))
    color_img_filter = skia.ImageFilters.Image(grade.rasterized(r))

    oval = DATPen().oval(r.inset(300)).f(hsl(0.5)).precompose(r)
    oval_img = oval.attrs["default"]["image"]["src"]
    (oval
        #.precompose(r)
        .attr(skp=dict(
            ImageFilter=skia.ImageFilters.DisplacementMap(
                skia.ColorChannel.kA,
                skia.ColorChannel.kG,
                50.0,
                skia.ImageFilters.Image(spots_img),
                skia.ImageFilters.Image(oval_img),
                skia.IRect(r.x, r.y, r.w, r.h)))))
    
    return oval

def release(passes):
    (FFMPEGExport(displacement, passes, loops=4)
        .h264()
        .write()
        .open())