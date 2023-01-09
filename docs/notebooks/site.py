from coldtype import *
from coldtype.notebook.parser import NotebookParser

root = Path(__FILE__).parent

build_dir = root / "site"
notebook_dir = root / "notebooks"
templates_dir = root / "templates"
assets_dir = root / "assets"

NotebookParser(notebook_dir, build_dir, templates_dir, assets_dir, do_nest=True, sort={
    None: [
        "introduction",
        "about",
        "overview",
        "install",
        "classes_functions",
        "tutorials",
        "cheatsheets",
    ],
    "tutorials": [
        "shapes",
        "geometry",
        "text",
        "animation",
        "drawbot",
        "blender",
        
    ],
    "cheatsheets": [
        "viewer",
        "easing",
        "rectangles",
        "oneletter",
        "text",
    ]
})

@renderable((100, 100), watch=[
    assets_dir/"style.css",
    templates_dir/"index.j2",
    templates_dir/"feed.j2",
    templates_dir/"post.j2",
    ])
def site(r):
    return P(r).f(0, 0.8, 0.3)