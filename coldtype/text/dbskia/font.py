import struct
from fontTools.ttLib import TTFont


def makeTTFontFromSkiaTypeface(skTypeface):
    ttf = TTFont(lazy=True)
    ttf.reader = SkiaSFNTReader(skTypeface)
    ttf._tableCache = None  # fonttools fix: doesn't get set when not reading from a file
    return ttf


class SkiaSFNTReader:

    def __init__(self, skTypeface):
        self.skTypeface = skTypeface
        self.tags = {intToTag(tagInt): tagInt for tagInt in skTypeface.getTableTags()}

    def __len__(self):
        return len(self.tags)

    def __contains__(self, tag):
        return tag in self.tags

    def keys(self):
        return self.tags.keys()

    def __getitem__(self, tag):
        if tag not in self.tags:
            raise KeyError(tag)
        return self.skTypeface.getTableData(self.tags[tag])


def intToTag(intTag):
    return struct.pack(">i", intTag).decode()


def tagToInt(tag):
    if isinstance(tag, str):
        tag = bytes(tag, "ascii")
    return struct.unpack(">i", tag)[0]