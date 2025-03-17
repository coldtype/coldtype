import math

from collections import defaultdict
from pathlib import Path

from coldtype.timing.timeline import Timeline, Timeable
from coldtype.timing.easing import ease, ez


try:
    import mido
except ImportError:
    mido = None


class MidiTimeline(Timeline):
    def __init__(self,
        path,
        duration=None,
        fps=30,
        bpm=None,
        track=0,
        rounded=True,
        lookup={},
        live=None
        ):
        if not mido:
            print("please install mido library")
            return

        def s2f(value):
            if rounded:
                return math.floor(value * fps)
            else:
                return value * fps

        midi_path = path if isinstance(path, Path) else Path(path).expanduser()
        self.midi_path = midi_path

        try:
            mid = mido.MidiFile(str(midi_path))
        except FileNotFoundError:
            print("FILE NOT FOUND", midi_path)
            mid = mido.MidiFile()
        
        events = []
        open_notes = []
        controls = {}
        
        self.mid = mid
        self.time_signature = (4, 4)

        if fps is None:
            fps = 30

        if bpm is None:
            bpm = float(mido.tempo2bpm(self.find_tempo()))

        for tidx, track in enumerate(mid.tracks):
            cumulative_time = 0
            events = []
            open_notes = {}
            for idx, msg in enumerate(track):
                if hasattr(msg, "note"):
                    delta_s = mido.tick2second(msg.time, mid.ticks_per_beat, mido.bpm2tempo(bpm))
                    cumulative_time += delta_s
                    o = open_notes.get(msg.note)
                    if o != None:
                        open_notes[msg.note] = None
                        timeable = Timeable(
                            s2f(o),
                            s2f(cumulative_time),
                            idx,
                            name=str(msg.note),
                            data=msg,
                            timeline=self,
                            track=tidx)
                        events.append(timeable)
                    
                    if msg.type == "note_on" and msg.velocity > 0:
                        open_notes[msg.note] = cumulative_time
                
                elif msg.is_cc():
                    delta_s = mido.tick2second(msg.time, mid.ticks_per_beat, mido.bpm2tempo(bpm))
                    cumulative_time += delta_s
                    frame = s2f(cumulative_time)

                    if msg.control not in controls:
                        controls[msg.control] = {}
                    
                    controls[msg.control][frame] = msg.value

        self.midi_file = mid
        self.bpm = bpm
        self.fps = fps
        self.controls = controls
        
        if controls:
            max_c_frame = 0
            for c, frames in controls.items():
                max_c_frame = max(max_c_frame, max(frames.keys()))
            self._duration = max_c_frame
        else:
            try:
                end = sorted(events, key=lambda e: e.end)[-1].end
                self._duration = int(duration or end)
            except IndexError:
                self._duration = 1
        
        try:
            self.min = min([int(n.name) for n in events])
            self.max = max([int(n.name) for n in events])
            self.notes = list(reversed(sorted(set(int(n.name) for n in events))))
            self.spread = self.max - self.min
        except ValueError:
            self.min = 0
            self.max = 0
            self.notes = []
            self.spread = 0

        self.lookup = {}
        if lookup:
            self.register(lookup)

        super().__init__(self._duration, self.fps, timeables=events)

        for t in self.timeables:
            t.track = self.notes.index(int(t.name))

    def __bool__(self):
        if self.midi_path.exists():
            return True
        else:
            return False

    @property
    def duration(self):
        return self._duration
    
    def find_tempo(self):
        for track in self.mid.tracks:
            for msg in track:
                if msg.type == "set_tempo":
                    return msg.tempo
                elif msg.type == "time_signature":
                    self.time_signature = (msg.numerator, msg.denominator)
        return 500000 # 120 equivalent
    
    def register(self, lookup):
        for k, v in lookup.items():
            self.lookup[k] = v
    
    def ki(self, key, fi=None):
        try:
            if key in self.lookup:
                return super().ki(self.lookup[key], fi)
        except TypeError:
            pass
        
        return super().ki(key, fi)
    
    def ci(self, control, default=0, fi=None):
        fi = self._norm_held_fi(fi)

        if control in self.controls:
            frames = self.controls[control]
            if fi in frames:
                return frames[fi]/127
            else:
                _fi = fi
                while _fi > 0:
                    if _fi in frames:
                        return frames[_fi]/127
                    _fi -= 1
                
                # _fi = fi
                # while _fi < self.duration:
                #     if _fi in frames:
                #         return frames[_fi]/127
                #     _fi += 1
        
        return default