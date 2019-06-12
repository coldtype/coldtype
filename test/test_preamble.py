import os
import sys
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.realpath(dirname + "/.."))
try:
    sys.path.insert(0, os.path.expanduser("~/Type/furniture"))
except:
    pass


def save_artifact(filename, content=None):
    p = dirname + "/artifacts/" + filename
    if not content:
        try:
            from drawBot import saveImage
            saveImage(p)
        except:
            print("No drawBot found, cannot save context to image")
    else:
        with open(p, "w") as f:
            f.write(content)