import subprocess

BLENDER = "/Applications/Blender.app/Contents/MacOS/blender"

def blend_frame(py_file, blend_file, expr, output_dir, fi):
    call = f"{BLENDER} -b {blend_file} --python-expr \"{expr}\" -o {output_dir}/ -f {fi}"
    print(f"Blending frame {fi}...")
    #print(call)
    #return
    #os.system(call)
    process = subprocess.Popen(call, stdout=subprocess.PIPE, shell=True)
    log = ""
    while True:
        out = process.stdout.read(1).decode("utf-8")
        log += out
        if out == "" and process.poll() != None:
            break
        if "Error: Python:" in log:
            print(log)
            process.kill()
            process.terminate()
            break

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