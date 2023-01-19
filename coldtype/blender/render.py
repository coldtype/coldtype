import subprocess, time, sys
from pathlib import Path

from coldtype.osutil import on_windows

def prefix_inline_venv(expr):
    vi = sys.version_info
    root = Path('.').absolute()

    if on_windows():
        venv = Path(f'./venv/Lib/site-packages').absolute()
    else:
        venv = Path(f'./venv/lib/python{vi.major}.{vi.minor}/site-packages').absolute()

    editable_egg_link = venv / "coldtype.egg-link"
    if editable_egg_link.exists():
        print("EXPANDING EGG LINK")
        root = Path(editable_egg_link.read_text().splitlines()[0])

    venv = venv.as_posix()
    root = root.as_posix()

    prefix = f"import sys; from pathlib import Path; sys.path.insert(0, '{venv}'); sys.path.insert(0, '{root}');"
    return prefix + " " + expr

def blender_launch_livecode(blender_app_path, file:Path, command_file):
    import os

    if not file.exists():
        file.parent.mkdir(exist_ok=True, parents=True)
    
    #call = f"{BLENDER} {file}"
    print(f"Opening blend file: {file}...")
    cf = Path(command_file).as_posix()
    args = [blender_app_path, file, "--python-expr", prefix_inline_venv(f"from coldtype.blender.watch import watch; watch('{cf}');")]
    return subprocess.Popen(args)


def blend_frame(blender_app_path, py_file, blend_file, expr, output_dir, fi):
    call = [
        str(blender_app_path),
        "-b", blend_file,
        "--python-expr", f"{expr}",
        "-o", f"{output_dir}####.png",
        "-f", str(fi),
    ]
    #call = f"{blender_app_path} -b \"{blend_file}\" --python-expr \"{expr}\" -o \"{output_dir}####.png\" -f {fi}"
    print(f"Blending frame {fi}...")
    print(call)
    #return
    #os.system(call)
    if True:
        process = subprocess.Popen(call, stdout=subprocess.PIPE, shell=False)
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
        print(log)
    else:
        print(subprocess.run(call, stdout=subprocess.PIPE, shell=True))
    print(f"/Blended frame {fi}.")

def blend_source(blender_app_path
    , py_file
    , blend_file
    , frame
    , output_dir
    , samples=-1
    , denoise=False
    ):
    """
    A facility for telling Blender to render a single frame in a background process
    """
    expr = prefix_inline_venv(f"from coldtype.blender.render import frame_render; frame_render(r'{py_file}', {frame}, {samples}, {denoise})")
    #print(expr)
    blend_frame(blender_app_path, py_file, blend_file, expr, output_dir, frame)

def frame_render(file, frame, samples=-1, denoise=False):
    """
    A facility for easy-rendering from within a backgrounded blender
    """
    import bpy
    from coldtype.renderer.reader import SourceReader
    from coldtype.blender import walk_to_b3d
    
    bpy.data.scenes[0].frame_set(frame)
    
    if samples > 0:
        bpy.data.scenes[0].cycles.samples = samples
    
    if denoise:
        bpy.data.scenes[0].cycles.denoiser = "OPENIMAGEDENOISE"
        bpy.data.scenes[0].cycles.use_denoising = True

    #time.sleep(1)

    sr = SourceReader(file)
    for r, res in sr.frame_results(frame, class_filters=[r"^b3d_.*$"]):
        if hasattr(r, "center"):
            walk_to_b3d(res, dn=True, renderable=r)
    sr.unlink()

    #time.sleep(1)