try:
    import cv2
except ImportError:
    print("You need to install opencv-python")

import tempfile
from pathlib import Path


def capture_frame(device_id=0, to=None):
    cam = cv2.VideoCapture(device_id)
    _, frame = cam.read()
    tf = None
    if to:
        tf = to
    else:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tf:
            pass
    
    cv2.imwrite(tf.name, frame)
    cam.release()
    return Path(tf.name)