from mojo.events import addObserver, removeObserver
from fontTools.pens.recordingPen import RecordingPen
from pathlib import Path
import json

class ColdtypeSerializer:
    def __init__(self):
        self.output = Path("~/robofont-coldtype.json").expanduser().absolute()
        addObserver(self, "shouldDraw", "draw")
    
    def unsubscribe(self):
        removeObserver(self, "draw")

    def shouldDraw(self, notification):
        glyph = notification['glyph']
        data_out = {"name": glyph.name, "layers": {}}
        for g in glyph.layers:
            rp = RecordingPen()
            g.draw(rp)
            data_out["layers"][g.layer.name] = dict(value=rp.value)
        self.output.write_text(json.dumps(data_out))

ColdtypeSerializer()