from coldtype import *
from subprocess import run

swear = Font.Find("SwearRomanVari")

def instance(self, output_path, remove_overlaps=False):
    print(">", self.variations)
    args = ["fonttools", "varLib.instancer", self.style.font.path.absolute()]
    
    for k,v in self.variations.items():
        args.append(f"{k}={v}")
    
    args.extend(["-o", output_path])
    
    if remove_overlaps:
        args.append("--remove-overlaps")
    
    print(args)
    run(args)
    return Font.Find(str(output_path))

StyledString.instance = instance

def subset(self, output_path):
    args = [
        "pyftsubset", str(self.path),
        f"--output-file={str(output_path)}",
        '--unicodes="U+0000-00FF U+2B22 U+201C U+201D"',
        "--ignore-missing-unicodes",
        "--ignore-missing-glyphs",
        "--notdef-outline",
    ]
    print(" ".join(args))
    os.system(" ".join(args))
    return Font.Find(str(output_path))

Font.subset = subset

@renderable((1080, 540), bg=1)
def viewer(r):
    txt = "“Hello World” øö Ħ"
    textface = StyledString(txt, Style(swear, 62, wght=0.45, opsz=0))
    instance = textface.instance(ººsiblingºº("SwearRomanCustom-instance.ttf"))
    subset = instance.subset(ººsiblingºº("SwearRomanCustom-subset.woff2"))

    return (P(
        textface.pens(),
        StSt(txt, instance, 62),
        StSt(txt, subset, 62),
        )
        .f(0)
        .stack(10)
        .align(r))