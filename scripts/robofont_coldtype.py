from mojo.events import addObserver, removeObserver
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import FloatingWindow, CheckBox, EditText
from fontTools.pens.recordingPen import RecordingPen
from pathlib import Path
import json

DEFAULT_PATH = "~/robofont-coldtype.json"

class ColdtypeSerializer(BaseWindowController):
    def __init__(self):
        self.w = FloatingWindow((300, 68), "Coldtype Serializer", minSize=(123, 200))
        self.w.globalToggle = CheckBox((10, 10, -10, 20), 'serialize?', value=True)
        self.w.pathBox = EditText((10, 34, -10, 22),
            text=DEFAULT_PATH,
            callback=self.editTextCallback)
        self.path = Path(DEFAULT_PATH).expanduser().absolute()
        addObserver(self, "shouldDraw", "fontWillSave")
        
        self.setUpBaseWindowBehavior()
        self.w.open()
        
        self.writeGlyph()
    
    def editTextCallback(self, sender):
        self.path = Path(sender.get()).expanduser().absolute()
    
    def windowCloseCallback(self, sender):
        removeObserver(self, 'fontWillSave')
        super(ColdtypeSerializer, self).windowCloseCallback(sender)
        
        self.writeGlyph()
    
    def writeGlyph(self):
        glyph = CurrentGlyph()
        image = glyph.image
        
        print(">>>> writeGlyph", glyph, image)
        
        data_out = {
            "font": CurrentFont().path,
            "name": glyph.name,
            "image": dict(offset=image.offset, scale=image.scale, fileName=image.__dict__["_wrapped"]["fileName"]),
            "layers": {}
        }
        
        for g in glyph.layers:
            rp = RecordingPen()
            g.draw(rp)

            contours = []
            for c in glyph.contours:
                contour = []
                for pt in c.points:
                    contour.append(dict(type=pt.type, x=pt.x, y=pt.y, smooth=pt.smooth, name=pt.name))
                contours.append(contour)

            data_out["layers"][g.layer.name] = dict(
                value=rp.value,
                width=g.width,
                contours=contours)
            
        self.path.write_text(json.dumps(data_out))

    def shouldDraw(self, notification):
        if not self.w.globalToggle.get():
            return
        
        self.writeGlyph()

ColdtypeSerializer()