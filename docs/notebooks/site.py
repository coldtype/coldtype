from coldtype import *
from coldtype.notebook.parser import NotebookParser

root = Path(__FILE__).parent

build_dir = root / "site"
notebook_dir = root / "notebooks"
templates_dir = root / "templates"
assets_dir = root / "assets"

NotebookParser(notebook_dir, build_dir, templates_dir, assets_dir)

@renderable((100, 100), watch=[
    assets_dir/"style.css",
    templates_dir/"index.j2",
    templates_dir/"feed.j2",
    templates_dir/"post.j2",
    ])
def site(r):
    return P(r).f(0, 0.8, 0.3)