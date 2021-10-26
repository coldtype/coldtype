from types import SimpleNamespace
import functools
import uharfbuzz as hb
from .font import intToTag, tagToInt


class GlyphInfo:

    def __init__(self, gid, name, cluster, dx, dy, ax, ay):
        self.gid = gid
        self.name = name
        self.cluster = cluster
        self.dx = dx
        self.dy = dy
        self.ax = ax
        self.ay = ay

    def __repr__(self):
        args = (f"{a}={repr(getattr(self, a))}"
                for a in ["gid", "name", "cluster", "dx", "dy", "ax", "ay"])
        return f"{self.__class__.__name__}({', '.join(args)})"


def getShapeFuncForSkiaTypeface(skTypeface):
    face = makeHBFaceFromSkiaTypeface(skTypeface)
    font = hb.Font(face)
    return functools.partial(_shape, face, font), face.upem


def makeHBFaceFromSkiaTypeface(skTypeface):
    tableData = {}
    tableTags = {intToTag(tag) for tag in skTypeface.getTableTags()}

    def getTable(face, tag, userData):
        if tag in tableData:
            return tableData[tag]
        if tag not in tableTags:
            return None
        data = skTypeface.getTableData(tagToInt(tag))
        # HB doesn't hold on the data, and neither does Skia, so we
        # need to do that ourselves.
        tableData[tag] = data
        return data

    return hb.Face.create_for_tables(getTable, None)


def _shape(face, font,
           text, fontSize=None,
           startPos=(0, 0), startCluster=0,
           flippedCanvas=False,
           *,
           features=None,
           variations=None,
           direction=None,
           language=None,
           script=None):
    if features is None:
        features = {}
    if variations is None:
        variations = {}

    if fontSize is None:
        fontScaleX = fontScaleY = 1
    else:
        fontScaleX = fontScaleY = fontSize / face.upem
    if flippedCanvas:
        fontScaleY = -fontScaleY

    font.scale = (face.upem, face.upem)
    font.set_variations(variations)

    hb.ot_font_set_funcs(font)

    buf = hb.Buffer.create()
    buf.add_str(text)  # add_str() does not accept str subclasses
    buf.guess_segment_properties()
    buf.cluster_level = hb.BufferClusterLevel.MONOTONE_CHARACTERS

    if direction is not None:
        buf.direction = direction
    if language is not None:
        buf.language = language
    if script is not None:
        buf.script = script

    hb.shape(font, buf, features)

    gids = [info.codepoint for info in buf.glyph_infos]
    clusters = [info.cluster + startCluster for info in buf.glyph_infos]
    positions = []
    startPosX, startPosY = startPos
    x = y = 0
    for pos in buf.glyph_positions:
        dx, dy, ax, ay = pos.position
        positions.append((
            startPosX + (x + dx) * fontScaleX,
            startPosY + (y + dy) * fontScaleY,
        ))
        x += ax
        y += ay
    endPos = startPosX + x * fontScaleX, startPosY + y * fontScaleY

    if True:
        infos = []
        for idx, gid in enumerate(gids):
            dx, dy = positions[idx]
            ax, ay = endPos[idx]
            infos.append(GlyphInfo(gid, "?", clusters[idx], dx, dy, ax, ay))
        return infos
    
    return SimpleNamespace(
        gids=gids,
        clusters=clusters,
        positions=positions,
        endPos=endPos,
    )


def scalePositions(positions, sx, sy=None):
    if sy is None:
        sy = sx
    return [(x * sx, y * sy) for x, y in positions]


def getFeatures(face, otTableTag):
    features = set()
    for scriptIndex, script in enumerate(hb.ot_layout_table_get_script_tags(face, otTableTag)):
        langIdices = list(range(len(hb.ot_layout_script_get_language_tags(face, otTableTag, scriptIndex))))
        langIdices.append(0xFFFF)
        for langIndex in langIdices:
            features.update(hb.ot_layout_language_get_feature_tags(face, otTableTag, scriptIndex, langIndex))
    return sorted(features)