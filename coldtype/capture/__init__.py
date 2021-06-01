try:
    import cv2
except ImportError:
    raise Exception("pip install opencv-python")

import skia
import numpy as np

def read_frame(cam):
    _, frame = cam.read()
    r_channel, g_channel, b_channel = cv2.split(frame)
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
    img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    return skia.Image.fromarray(img_BGRA)