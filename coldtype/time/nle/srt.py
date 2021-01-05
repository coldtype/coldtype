import srt, re
from timecode import Timecode
from datetime import datetime

from coldtype.time.sequence import Sequence, Clip, ClipTrack

def srt_to_frame(fps, st):
    tc = Timecode(fps,
        srt.timedelta_to_srt_timestamp(st).replace(",", "."))
    return tc.frame_number-86400-21600

class SRT(Sequence):
    def __init__(self, path, fps, storyboard=None, workarea_track=0):
        self.path = path
        subs = srt.parse(path.read_text())
        clips = []

        for sidx, s in enumerate(subs):
            clips.append(Clip(
                re.sub(r"<[^>]+>", "", s.content).strip(),
                srt_to_frame(fps, s.start),
                srt_to_frame(fps, s.end),
                idx=sidx,
                track=0))
        
        track = ClipTrack(self, clips, [])
        super().__init__(track.duration(), fps, storyboard, [track])