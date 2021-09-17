import os, cv2, sys, traceback
from pathlib import Path
from coldtype.renderer.reader import SourceReader
from coldtype.renderer.state import RendererState
from coldtype.renderer.utils import bcolors, bc_print

rs = RendererState(None)
rs.cv2caps[0] = cv2.VideoCapture(0)

directory = sys.argv[1]

try:
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = Path(root + "/" + file)
            if path.suffix in [".py", ".rst", ".md"] and not path.name.startswith("_"):
                print(path, "...")
                try:
                    for r, res in SourceReader.FrameResult(path, 0, renderer_state=rs):
                        print("    >", r.name)
                except Exception as e:
                    if "Intentional" not in str(e):
                        raise e

except Exception as e:
    stack = traceback.format_exc()
    print(stack)
    print(e)
    bc_print(bcolors.FAIL, "FAILED")
finally:
    for _, cv2cap in rs.cv2caps.items():
        cv2cap.release()