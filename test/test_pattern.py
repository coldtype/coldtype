from coldtype import *

@renderable((1000, 1000))
def test_pattern_generate(r):
    return (DATPen()
        .rect(r.inset(250))
        .rotate(45)
        .flatten()
        .roughen(150)
        .f(hsl(0.7, 0.7, 0.7)))

@renderable((1000, 1000))
def test_pattern_use(r):
    imgp = test_pattern_generate.last_passes[0].output_path
    return (DATPen()
        .rect(r)
        .f(1)
        .img(imgp, r.take(50, "mdx").square()))