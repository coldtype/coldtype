from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.transformPen import TransformPen


def flipped_svg_pen(recording, height):
    svg_pen = SVGPathPen(None)
    flip_pen = TransformPen(svg_pen, (1, 0, 0, -1, 0, height))
    #flipped = []
    #for t, pts in recording.value:
    #    flipped.append((t, [(round(x, 1), round(height-y, 1)) for x, y in pts]))
    #replayRecording(flipped, flip_pen)
    replayRecording(recording.value, flip_pen)
    return svg_pen


def pen_to_svg(recording, rect):
    svg_pen = flipped_svg_pen(recording, rect.h)
    return f"""
    <svg width="{rect.w}" height="{rect.h}" xmlns="http://www.w3.org/2000/svg">
        <path d="{svg_pen.getCommands()}"/>
    </svg>
    """


def pen_to_html(recording, rect):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<style>
    body {{ background: #eee; }}
    svg {{
        position: absolute;
        top: 10px;
        right: 10px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        background: white;
    }}
</style>
</head>
<body>
    {pen_to_svg(recording, rect)}
</body>
</html>
    """
