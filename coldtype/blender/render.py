import os

BLENDER = "/Applications/Blender.app/Contents/MacOS/blender"

def blend_frame(file, expr, output_dir, fi):
    os.system(f"{BLENDER} -b scratch.blend --python-expr \"{expr}\" -o {output_dir}/ -f {fi}")

def blend_pickle(file, pickle, output_dir, samples=2):
    fi = int(pickle.stem.split("_")[-1])
    expr = f"import bpy; bpy.data.scenes[0].cycles.samples = {samples}; from coldtype.blender import DATPen, _walk_to_b3d; _walk_to_b3d(DATPen().Unpickle('{pickle}'), dn=True)"
    blend_frame(file, expr, output_dir, fi)