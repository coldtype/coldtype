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
    
    def Unpickle(self, src):
        if isinstance(src, str):
            src = Path(src)
        return pickle.load(open(str(src.expanduser()), "rb"))
    
    def withJSONValue(self, path, keys=None):
        data = json.loads(Path(path).expanduser().read_text())
        if keys is not None:
            for key in keys:
                data = data[key]
        
        self._val.value = data
        return self
    
    def withSVG(self, svg):
        from fontTools.svgLib import SVGPath
        svg = SVGPath.fromstring(svg)
        rp = RecordingPen()
        svg.draw(rp)
        self._val.value = rp.value
        return self

    def withSVGFile(self, svg_file):
        svg_file = Path(svg_file).expanduser().absolute()
        from fontTools.svgLib import SVGPath
        svg = SVGPath.fromstring(svg_file.read_bytes())
        rp = RecordingPen()
        svg.draw(rp)
        self._val.value = rp.value
        return self