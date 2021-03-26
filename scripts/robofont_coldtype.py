from mojo.events import addObserver, removeObserver
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import FloatingWindow, CheckBox
from fontTools.pens.recordingPen import RecordingPen
from pathlib import Path
import json

class ColdtypeSerializer(BaseWindowController):
    def __init__(self):
        self.w = FloatingWindow((300, 40), "Coldtype Serializer", minSize=(123, 200))
        self.w.globalToggle = CheckBox((10, 10, -10, 20), 'serialize?', value=True)
        self.output = Path("~/robofont-coldtype.json").expanduser().absolute()
        addObserver(self, "shouldDraw", "fontWillSave")
        
        self.setUpBaseWindowBehavior()
        self.w.open()
    
    def windowCloseCallback(self, sender):
        removeObserver(self, 'fontWillSave')
        super(ColdtypeSerializer, self).windowCloseCallback(sender)

    def shouldDraw(self, notification):
        if not self.w.globalToggle.get():
            return
        #glyph = notification['glyph']
        glyph = CurrentGlyph()
        data_out = {"name": glyph.name, "layers": {}}
        for g in glyph.layers:
            rp = RecordingPen()
            g.draw(rp)
            data_out["layers"][g.layer.name] = dict(value=rp.value, width=g.width)
        self.output.write_text(json.dumps(data_out))
        print("> wrote glyph data", glyph.name)

ColdtypeSerializer()