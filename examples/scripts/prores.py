from coldtype import *
from coldtype.renderable.animation import image_sequence, shutil

def sorted_images(folder, suffix="*.jpg"):
    return list(sorted(folder.glob(suffix), key=lambda p: p.name))

folder = Path(__inputs__[0])

images = sorted_images(folder)
images_hires = None

for img in images:
    print(img)

if (folder / "hires").exists():
    images_hires = sorted_images(folder / "hires")

parent = folder.parent
base_name = parent.name + "_" + folder.name
name = base_name

fps = 12

if images_hires:
    name = base_name + "_proxy"
    @image_sequence(images_hires, fps, looping=True, name=base_name, render_only=True)
    def viewer_hires(_): return None

@image_sequence(images, fps, looping=False, name=name)
def viewer(_): return None

def release(_):
    FFMPEGExport(viewer, loops=1, output_folder=parent).prores().write(True)
    if images_hires:
        FFMPEGExport(viewer_hires, loops=1, output_folder=parent).prores().write(True)
    
    if True:
        # clean up unnecessary files
        shutil.rmtree(viewer.output_folder)
        if images_hires:
            shutil.rmtree(viewer_hires.output_folder)