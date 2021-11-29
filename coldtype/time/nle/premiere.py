import json
from pathlib import Path

# import extra stuff for convenience in user code
from coldtype.time.sequence import Marker, ClipTrack, Clip, Sequence, ClipGroup, ClipGroupPens


VIDEO_OFFSET = 86313 # why is this?

group_pens_cache = {}

def to_frames(seconds, fps):
    frames = int(round(float(seconds)*fps))
    if frames >= VIDEO_OFFSET:
        frames -= VIDEO_OFFSET
    return frames


class PremiereTimeline(Sequence):
    __name__ = "Premiere"

    def __init__(self, path, storyboard=None, duration_override=None, workarea_track=0):
        self.path = path

        json_path = path if isinstance(path, Path) else Path(path).expanduser()

        try:
            jsondata = json.loads(json_path.read_text())
        except:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(json_path.read_text())
            raise Exception("NOPE")
            jsondata = {}

        meta = jsondata.get("metadata")        
        fps = 1 / meta.get("frameRate")
        duration = int(round(int(meta.get("duration"))/int(meta.get("timebase"))))

        if duration_override:
            duration = duration_override

        self.start = 0
        self.end = duration

        tof = lambda s: int(round(float(s)*fps))
        
        cti = tof(meta.get("cti", 0))
        self.cti = cti

        _storyboard = []
        _storyboard.append(self.cti)
        for m in jsondata.get("storyboard"):
            f = tof(m.get("start"))
            if f not in _storyboard:
                _storyboard.append(f)
        
        if storyboard:
            _storyboard = storyboard
        
        workareas = []
        workareas.append(range(max(0, tof(meta.get("inPoint"))), tof(meta.get("outPoint"))+1))
        self.workareas = workareas

        tracks = []
        for tidx, track in enumerate(jsondata.get("tracks")):
            markers = []
            for marker in track.get("markers"):
                markers.append(Marker(
                    to_frames(marker.get("start"), fps),
                    to_frames(marker.get("end"), fps),
                    marker))
            
            clips = []
            for cidx, clip in enumerate(track.get("clips")):
                clips.append(Clip(
                    clip.get("name"),
                    to_frames(clip.get("start"), fps),
                    to_frames(clip.get("end"), fps),
                    idx=cidx,
                    track=tidx))
            
            tracks.append(ClipTrack(self, clips, markers))
        
        super().__init__(duration, fps, _storyboard, tracks, workarea_track=workarea_track)