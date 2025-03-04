from enum import Enum, auto

try:
    import skia
except ImportError:
    skia = None


class BlendMode(Enum):
    Clear = auto()
    Src = auto()
    Dst = auto()
    SrcOver = auto()
    DstOver = auto()
    SrcIn = auto()
    DstIn = auto()
    SrcOut = auto()
    DstOut = auto()
    SrcATop = auto()
    DstATop = auto()
    Xor = auto()
    Plus = auto()
    Modulate = auto()
    Screen = auto()
    Overlay = auto()
    Darken = auto()
    Lighten = auto()
    ColorDodge = auto()
    ColorBurn = auto()
    HardLight = auto()
    SoftLight = auto()
    Difference = auto()
    Exclusion = auto()
    Multiply = auto()
    Hue = auto()
    Saturation = auto()
    Color = auto()
    Luminosity = auto()
    
    def to_skia(self):
        return _SKIA_MAPPING[self.value-1]
    
    def print(self):
        print(self.name)
        return self

    @staticmethod
    def Cycle(i, show=False):
        bms = list(BlendMode)
        match = bms[i%len(bms)]
        if show:
            print(match)
        return match

if not skia:
    _SKIA_MAPPING = []
else:
    _SKIA_MAPPING = [
        skia.BlendMode.kClear,
        skia.BlendMode.kSrc,
        skia.BlendMode.kDst,
        skia.BlendMode.kSrcOver,
        skia.BlendMode.kDstOver,
        skia.BlendMode.kSrcIn,
        skia.BlendMode.kDstIn,
        skia.BlendMode.kSrcOut,
        skia.BlendMode.kDstOut,
        skia.BlendMode.kSrcATop,
        skia.BlendMode.kDstATop,
        skia.BlendMode.kXor,
        skia.BlendMode.kPlus,
        skia.BlendMode.kModulate,
        skia.BlendMode.kScreen,
        skia.BlendMode.kOverlay,
        skia.BlendMode.kDarken,
        skia.BlendMode.kLighten,
        skia.BlendMode.kColorDodge,
        skia.BlendMode.kColorBurn,
        skia.BlendMode.kHardLight,
        skia.BlendMode.kSoftLight,
        skia.BlendMode.kDifference,
        skia.BlendMode.kExclusion,
        skia.BlendMode.kMultiply,
        skia.BlendMode.kHue,
        skia.BlendMode.kSaturation,
        skia.BlendMode.kColor,
        skia.BlendMode.kLuminosity]

if __name__ == "__main__":
    print(BlendMode.Saturation.to_skia())