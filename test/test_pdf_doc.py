from coldtype import *
import skia

#@renderable(fmt="pdf")
def test_onepage(r):
    return (DATPen().oval(r.inset(50)).f(hsl(0.95)))

class pdfdoc(animation):
    def __init__(self, rect=Rect("letter"), **kwargs):
        super().__init__(rect=rect, fmt="pickle", rasterizer="pickle", **kwargs)

    def package(self, filepath, output_folder):
        pdf_path = filepath.parent / ("pdfs/" + filepath.stem + ".pdf")
        pickles = list(sorted(self.output_folder.glob("*.pickle")))
        print(pickles)
        

@pdfdoc()
def test_multipage(f):
    return (DATPen()
        .rect(f.a.r.inset(50))
        .f(hsl(f.a.progress(f.i).e)))