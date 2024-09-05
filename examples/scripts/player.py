from coldtype import *
from coldtype.renderable.animation import image_sequence, shutil

def sorted_images(folder, suffix="*.jpg"):
    return list(sorted(folder.glob(suffix), key=lambda p: p.name))

folder = Path(__inputs__[0])
fps = int(__inputs__[1])

images = sorted_images(folder)

parent = folder.parent
base_name = parent.name + "_" + folder.name
name = base_name

@image_sequence(images, fps, looping=True, name=name)
def viewer(_): return None

def release(_):
    FFMPEGExport(viewer, loops=1, output_folder=parent).prores().write(True)    
    if True:
        shutil.rmtree(viewer.output_folder)