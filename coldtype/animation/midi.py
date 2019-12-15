import mido
import math

from coldtype.animation.timeline import Timeline

class MidiNote():
    def __init__(self, note, on, off, fps, rounded):
        self.fps = fps
        self.note = note
        self.on_seconds = on
        self.off_seconds = off
        self.rounded = rounded
        self.on = self.onf(rounded=rounded)
        self.off = self.offf(rounded=rounded)
        self.duration = self.off - self.on

    def s_to_f(self, value, rounded=True, fps=None):
        _fps = fps or self.fps
        if rounded:
            return math.floor(value*_fps)
        else:
            return value*_fps
    
    def onf(self, rounded=True, fps=None):
        return self.s_to_f(self.on_seconds, rounded=rounded, fps=fps)
    
    def offf(self, rounded=True, fps=None):
        return self.s_to_f(self.off_seconds, rounded=rounded, fps=fps)


class MidiTrack():
    def __init__(self, notes, name=None):
        self.notes = notes
        self.name = name
    
    def noteForFrame(self, note_numbers, frame, preverb=0, reverb=0):
        if isinstance(note_numbers, int):
            note_numbers = [note_numbers]
        for note in reversed(self.notes):
            valid = False
            if callable(note_numbers):
                if note_numbers(note.note):
                    valid = True
            else:
                if note_numbers == "*" or note.note in note_numbers:
                    valid = True
            
            if valid and frame >= (note.on-preverb) and frame < (note.off+reverb):
                return note
    
    def valueForFrame(self, note_numbers, frame, preverb=0, reverb=0):
        note = self.noteForFrame(note_numbers, frame, preverb=preverb, reverb=reverb)
        if note:
            v = 1 - ((frame - note.on) / (note.duration+reverb))
            if v > 1:
                v = 2 + ((frame - note.on - preverb) / preverb)
                print(v)
            return v
        else:
            return 0
    
    def countToFrame(self, note_number, frame, preverb=0):
        count = 0
        for note in self.notes:
            if note.note == note_number:
                if frame >= (note.on-preverb):
                    count += 1
        return count


class MidiTimeline(Timeline):
    __name__ = "Midi"

    def __init__(self, tracks):
        self.tracks = tracks
        all_notes = []
        for t in tracks:
            for note in t.notes:
                all_notes.append(note.note)
        self.min = min(all_notes)
        self.max = max(all_notes)
        duration = 100
        fps = 30
        storyboard = [0] # possible, just an arg?
        #workareas = [] # possible, just an arg?
        super().__init__(duration, fps=fps, storyboard=storyboard)

    def ReadFromFile(f, fps=30, bpm=120, rounded=True):
        mid = mido.MidiFile(str(f))
        events = {}
        open_notes = {}
        for i, track in enumerate(mid.tracks):
            time = 0
            cumulative_time = 0
            events[track.name] = []
            open_notes[track.name] = {}
            for idx, msg in enumerate(track):
                if hasattr(msg, "note"):
                    delta_s = mido.tick2second(msg.time, mid.ticks_per_beat, mido.bpm2tempo(bpm))
                    cumulative_time += delta_s
                    o = open_notes.get(track.name).get(msg.note)
                    if o != None:
                        open_notes[track.name][msg.note] = None
                        events[track.name].append(MidiNote(msg.note, o, cumulative_time, fps, rounded))
                    if msg.type == "note_on" and msg.velocity > 0:
                        open_notes[track.name][msg.note] = cumulative_time
        tracks = []
        for track_name, es in events.items():
            tracks.append(MidiTrack(es, name=track_name))
        return MidiTimeline(tracks)
    
    def ReadFromFiles(root, filesnames):
        pass