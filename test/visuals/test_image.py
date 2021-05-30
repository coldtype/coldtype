from coldtype import *

@renderable()
def test_image_gen(r):
    return (DATPen()
        .oval(r.take(0.5, "mdx"))
        .xor(DATPen()
            .rect(r.inset(200)))
        .f(Gradient.V(r, hsl(0.5), hsl(0.8)))
        .rotate(45)
        .scale(0.9))

@renderable((1000, 500))
def test_resize(r):
    imgp = test_image_gen.last_passes[0].output_path
    img = SkiaPen.ReadImage(imgp)
    return (DATPen()
        .rect(r)
        .img(img, r.take(0.5, "mdx").square(), 0)
        .f(0))
