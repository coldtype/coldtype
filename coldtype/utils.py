from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.transformPen import TransformPen
import re

def spinalcase(s):
    return re.sub(r"[A-Z]{1}", lambda c: f"-{c.group().lower()}", s)


def flipped_svg_pen(recording, height):
    svg_pen = SVGPathPen(None)
    flip_pen = TransformPen(svg_pen, (1, 0, 0, -1, 0, height))
    replayRecording(recording.value, flip_pen)
    return svg_pen


def pen_to_svg(recording, rect, **kwargs):
    svg_pen = flipped_svg_pen(recording, rect.h)
    attr_string = " ".join([f"{spinalcase(k)}='{v}'" for k,v in kwargs.items()])
    return f"""
<path {attr_string} d="{svg_pen.getCommands()}"/>
    """

def wrap_svg_paths(paths, rect):
    return f"""
    <svg width="{rect.w}" height="{rect.h}" viewBox="0 0 {rect.w} {rect.h}" xmlns="http://www.w3.org/2000/svg">
        {"".join(paths)}
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
