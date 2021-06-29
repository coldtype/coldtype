import os

from numpy.lib.arraysetops import isin

BLENDER = "/Applications/Blender.app/Contents/MacOS/blender"

def blend_frame(py_file, blend_file, expr, output_dir, fi):
    call = f"{BLENDER} -b {blend_file} --python-expr \"{expr}\" -o {output_dir}/ -f {fi}"
    #print(call)
    os.system(call)

# def blend_pickle(file, pickle, output_dir, samples=2):
#     fi = int(pickle.stem.split("_")[-1])
#     expr = f"import bpy; bpy.data.scenes[0].cycles.samples = {samples}; from coldtype.blender import DATPen, _walk_to_b3d; _walk_to_b3d(DATPen().Unpickle('{pickle}'), dn=True)"
#     blend_frame(file, expr, output_dir, fi)

def blend_source(py_file, blend_file, frame, output_dir, samples=2):
    expr = f"from coldtype.blender.render import frame_render; frame_render('{py_file}', {frame}, {samples})"
    #print(expr)
    blend_frame(py_file, blend_file, expr, output_dir, frame)

def frame_render(file, frame, samples):
    import bpy
    from coldtype.renderer.reader import SourceReader
    from coldtype.blender import _walk_to_b3d
    bpy.data.scenes[0].cycles.samples = samples
    sr = SourceReader(file)
    for r, res in sr.frame_results(frame):
        if "b3d" in r.__class__.__name__:
            _walk_to_b3d(res)
    sr.unlink()