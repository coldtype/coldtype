from coldtype import *
import zipfile, requests, io, subprocess, sys, shutil

file = Path(ººFILEºº)
zip_filename = "glfw-3.4.bin.MACOS"
zip_src = f"https://github.com/glfw/glfw/releases/download/3.4/{zip_filename}.zip"
zip_dst = file.parent

@renderable()
def glfw34(r):
    if not (zip_dst / zip_filename).exists():
        print("downloading...")
        r = requests.get(zip_src)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(zip_dst)

    glfw_src = zip_dst / zip_filename
    dylib_src = glfw_src / "lib-universal/libglfw.3.dylib"
    print(dylib_src)
    if dylib_src.exists():
        print("yes")
    
    vi = sys.version_info
    dylib_dst = Path(sys.executable).parent.parent / f"lib/python{vi.major}.{vi.minor}/site-packages/glfw/libglfw.3.dylib"

    if not dylib_dst.exists():
        print("could not find glfw installation")
    else:
        shutil.copyfile(dylib_src, dylib_dst)

    # p1 = subprocess.Popen(["which", "python"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = p1.communicate()
    # which_python = out.strip()
    # p2 = subprocess.Popen([which_python, "-c", "import sysconfig;print(sysconfig.get_config_var('installed_base'))"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = p2.communicate()
    # installed_base = out.strip()
    # if isinstance(installed_base, bytes):
    #     installed_base = installed_base.decode("utf-8")
    
    # print(which_python, installed_base)

    return None