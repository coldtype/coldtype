import os, cv2
from pathlib import Path
from coldtype.renderer.reader import SourceReader
from coldtype.renderer.state import RendererState
from coldtype.renderer.utils import bcolors, bc_print

rs = RendererState(None)
rs.cv2caps[0] = cv2.VideoCapture(0)

try:
    for root, dirs, files in os.walk("examples"):
        for file in files:
            path = Path(root + "/" + file)
            if path.suffix in [".py", ".rst", ".md"]:
                print(path, "...")
                for r, res in SourceReader.FrameResult(path, 0, renderer_state=rs):
                    print("    >", r.name)
                    # try:
                    #     res.picklejar(r.rect)
                    # except:
                    #     pass
except Exception as e:
    print(e)
    bc_print(bcolors.FAIL, "FAILED")
finally:
    for _, cv2cap in rs.cv2caps.items():
        cv2cap.release()