from fontTools.pens.recordingPen import RecordingPen, replayRecording
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform


def transformpen(pen, transform):
    op = RecordingPen()
    tp = TransformPen(op, transform)
    replayRecording(pen.value, tp)
    return op