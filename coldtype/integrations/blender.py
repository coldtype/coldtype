from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile
from coldtype.pens.datpen import DATPens
from coldtype.pens.datimage import DATImage
from functools import partial

class BlenderRenderConfig():
    def __init__(self,
        blend_file:Path,
        render_dir:Path,
        blender_version="2.92",
        blender_app_path="/Applications/Blender.app/Contents/MacOS/blender"
        ):

        self.blend_file = blend_file
        self.render_dir = render_dir
        self.blender_version = blender_version
        self.blender_app_path = blender_app_path

        self.render_dir.parent.mkdir(exist_ok=True, parents=True)

    def blend_fn(self, index, silent=True, skip=False):
        def blend(pens):
            code = (Path(__file__).parent / "blender_script_template.py").read_text()

            code = code.replace("$BLENDER_VERSION", self.blender_version)
            
            if not hasattr(pens, "_pens"):
                pens = DATPens([pens])
            
            print(">", pens)
            codeds = []

            def write_pen(i, p):
                print(">>>", p)
                coda = [
                    ".tag('Test')",
                    ".cast(BlenderPen)",
                    ".draw(tc)",
                ]
                if "blenderpen" in p.data:
                    for k, v in p.data.get("blenderpen").items():
                        vs = [str(v) for v in v]
                        coda.append(f".{k}({','.join(vs)})")
                coded = p.to_code("DraftingPen", coda)
                codeds.append(coded)
                
            pens.pmap(write_pen)
            code += "\n".join(codeds)
            
            with NamedTemporaryFile(mode="w", suffix="coldtype_blender_code.py", delete=False) as tf:
                tf.write(code)

            print("================")
            print(code)
            print("================")

            out_dir = self.render_dir
            args = [self.blender_app_path,
                "-b", str(self.blend_file),
                "-P", str(tf.name),
                "-o", f"{str(out_dir)}/frame_",
                "-f", str(index)]
            if not skip:
                print("blendering start>")
                output = run(args, capture_output=silent)
                print("<blendering end")
            else:
                print("skipping blender", args)
            #print(output)
            file = out_dir / "frame_{:04d}.png".format(index)
            print(file)
            return DATImage(file)
            return pens[0]
        
        return blend