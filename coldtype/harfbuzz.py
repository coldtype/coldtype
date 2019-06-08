import uharfbuzz as hb
from furniture.geometry import Rect


class HarfbuzzFrame():
    def __init__(self, info, position, frame):
        self.gid = info.codepoint
        self.info = info
        self.position = position
        self.frame = frame

    def __repr__(self):
        return f"HarfbuzzFrame: gid{self.gid}@{self.frame}"


class Harfbuzz():
    def __init__(self, font_path):
        with open(font_path, 'rb') as fontfile:
            self.fontdata = fontfile.read()
        self.fontPath = font_path
        
        #self.font = hb.Font(self.face)
        #self.upem = int(self.face.upem)
        face = hb.Face(self.fontdata)
        self.upem = int(face.upem)
        #self.upem = self.face.upem
        #self.font.scale = (self.upem, self.upem)
        #hb.ot_font_set_funcs(self.font)

    def getFrames(self, text="", axes=dict(), features=dict(kern=True, liga=True), height=1000):
        face = hb.Face(self.fontdata)
        font = hb.Font(face)
        font.scale = (face.upem, face.upem)
        hb.ot_font_set_funcs(font)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        
        if len(axes.items()) > 0:
            font.set_variations(axes)
        
        hb.shape(font, buf, features)
        infos = buf.glyph_infos
        positions = buf.glyph_positions
        frames = []
        x = 0
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            cluster = info.cluster
            x_advance = pos.x_advance
            x_offset = pos.x_offset
            y_offset = pos.y_offset
            frames.append(HarfbuzzFrame(info, pos, Rect((x+x_offset, y_offset, x_advance, height)))) # 100?
            x += x_advance
        return frames