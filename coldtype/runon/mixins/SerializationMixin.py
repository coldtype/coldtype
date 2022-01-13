import pickle, json

from pathlib import Path
from fontTools.pens.recordingPen import RecordingPen

from coldtype.geometry import Rect


class SerializationMixin():
    def pickle(self, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        fh = open(str(dst), "wb")
        
        def prune(pen, state, data):
            if state >= 0:
                if hasattr(pen, "_stst"):
                    pen._stst = None
        
        self.walk(prune)
        pickle.dump(self, fh)
        fh.close()
        return self
    
    def picklejar(self, rect=Rect(1000, 1000), name=None):
        if not name:
            from uuid import uuid4
            name = str(uuid4())
        
        p = Path(f"~/.coldtype/picklejar/{name}.pickle").expanduser()
        p.parent.mkdir(exist_ok=True)
        (self.data(rect=rect).pickle(Path(p)))
        return self
    
    def Unpickle(self, src):
        if isinstance(src, str):
            src = Path(src)
        return pickle.load(open(str(src.expanduser()), "rb"))
    
    def withJSONValue(self, path):
        self._val.value = json.loads(Path(path)
            .expanduser()
            .read_text())
        return self
    
    def withSVGFile(self, svg_file):
        from fontTools.svgLib import SVGPath
        svg = SVGPath.fromstring(svg_file.read_bytes())
        rp = RecordingPen()
        svg.draw(rp)
        self._val.value = rp.value
        return self