from coldtype import *
import skia, pickle

@renderable(fmt="pdf")
def test_onepage(r):
    return (DATPen().oval(r.inset(50)).f(hsl(0.95)))

class pdfdoc(animation):
    def __init__(self, rect=Rect("letter"), **kwargs):
        super().__init__(rect=rect, fmt="pickle", rasterizer="pickle", **kwargs)

    def package(self, filepath, output_folder):
        pdf_path = filepath.parent / ("pdfs/" + filepath.stem + ".pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pickles = list(sorted(self.output_folder.glob("*.pickle")))
        pages = DATPens()
        for pk in pickles:
            pages += pickle.load(open(pk, "rb"))
        SkiaPen.PDFMultiPage(pages, self.rect, str(pdf_path))
        
@pdfdoc()
def test_multipage(f):
    return (DATPen()
        .rect(f.a.r.inset(50))
        .f(hsl(f.a.progress(f.i).e)))