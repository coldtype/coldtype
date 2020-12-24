from coldtype import *
import coldtype.filtering as fl

def improved(e, xo=0, yo=0, xs=1, ys=1, base=1):
    noise = skia.PerlinNoiseShader.MakeImprovedNoise(0.015, 0.015, 3, base)
    matrix = skia.Matrix()
    matrix.setTranslate(e*xo, e*yo)
    matrix.setScaleX(xs)
    matrix.setScaleY(ys)
    return noise.makeWithLocalMatrix(matrix)

@animation(bg=0, timeline=Timeline(120, fps=30))
def displacement(f):
    r = f.a.r
    spots = (DATPen()
        .f(1)
        #.oval(r.inset(300))
        .precompose(r)
        .attr(skp=dict(
            #PathEffect=skia.DiscretePathEffect.Make(5.0, 15.0, 0),
            Shader=improved(0, xo=300, yo=200, xs=1.15, ys=1.15, base=random()*1000).makeWithColorFilter(fl.compose(
                fl.fill(bw(1)),
                fl.as_filter(fl.contrast_cut(110, 1)), # heighten contrast
                skia.LumaColorFilter.Make(), # knock out
            )),
        ))
        .phototype(r, fill=bw(1), cut=130, blur=5, cutw=10))
    
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
