import skia
from blackrenderer.backends.skia import _unpackColorLine, _extendModeMap

class SkiaShaders():
    @staticmethod
    def drawPathLinearGradient(colorLine, pt1, pt2, extendMode, gradientTransform) -> skia.GradientShader:
        matrix = skia.Matrix()
        matrix.setAffine(gradientTransform)
        colors, stops = _unpackColorLine(colorLine)
        return skia.GradientShader.MakeLinear(
            points=[pt1, pt2],
            colors=colors,
            positions=stops,
            mode=_extendModeMap[extendMode],
            localMatrix=matrix,
        )
    
    @staticmethod
    def drawPathSweepGradient(
        colorLine,
        center,
        startAngle,
        endAngle,
        extendMode,
        gradientTransform,
    ):
        # The following is needed to please the Skia shader, but it's a bit fuzzy
        # to me how this affects the spec. Translated from:
        # https://source.chromium.org/chromium/chromium/src/+/master:third_party/skia/src/ports/SkFontHost_FreeType_common.cpp;l=673-686
        startAngle %= 360
        endAngle %= 360
        if startAngle >= endAngle:
            endAngle += 360
        matrix = skia.Matrix()
        matrix.setAffine(gradientTransform)
        colors, stops = _unpackColorLine(colorLine)
        return skia.GradientShader.MakeSweep(
            cx=center[0],
            cy=center[1],
            colors=colors,
            positions=stops,
            mode=_extendModeMap[extendMode],
            startAngle=startAngle,
            endAngle=endAngle,
            localMatrix=matrix,
        )
    
    @staticmethod
    def drawPathRadialGradient(
        colorLine,
        startCenter,
        startRadius,
        endCenter,
        endRadius,
        extendMode,
        gradientTransform,
    ):
        matrix = skia.Matrix()
        matrix.setAffine(gradientTransform)
        colors, stops = _unpackColorLine(colorLine)
        return skia.GradientShader.MakeTwoPointConical(
            start=startCenter,
            startRadius=startRadius,
            end=endCenter,
            endRadius=endRadius,
            colors=colors,
            positions=stops,
            mode=_extendModeMap[extendMode],
            localMatrix=matrix,
        )