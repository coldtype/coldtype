from coldtype.test import *
import coldtype.filtering as fl

obv = Font.Cacheable("~/Type/fonts/fonts/ObviouslyVariable.ttf")

def improved(e, xo=0, yo=0, xs=1, ys=1, base=1):
    noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.015, 0.015, 3, base)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)

@animation((1500, 800), bg=hsl(0.8), timeline=Timeline(120, fps=24), composites=1, bg_render=True)
def displacement(f):
    r = f.a.r
    spots = (DATPen()
        .f(1)
        #.oval(r.inset(300))
        .precompose(r)
        .attr(skp=dict(
            #PathEffect=skia.DiscretePathEffect.Make(5.0, 15.0, 0),
            Shader=improved(1, xo=300, yo=200, xs=10.15, ys=2.15, base=f.i/30).makeWithColorFilter(fl.compose(
                fl.fill(bw(0)),
                fl.as_filter(fl.contrast_cut(210, 1)), # heighten contrast
                skia.LumaColorFilter.Make(), # knock out
            )),
        )))
    

    spots = (DATPenSet([
            displacement.last_result if f.i != -1 else None,
            DATPen().rect(r).f(1, 0.01),
            #spots,
            StyledString("OK", Style(obv, 500, ro=1, wght=0.5, wdth=f.a.progress(f.i, easefn=["ceio"], loops=5).e)).pen().f(0).s(1).sw(7).align(f.a.r).translate(0, -600+f.i*10),
        ]).color_phototype(r.inset(0), cut=130, blur=3, cutw=20))
    
    return spots
    
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
    displacement.write_gif(passes)