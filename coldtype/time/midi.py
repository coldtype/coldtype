import mido, math
from pathlib import Path

from coldtype.time.timeline import Timeline
from coldtype.time.easing import ease


class MidiNote():
    def __init__(self, note, on, off, fps, rounded, idx):
        self.fps = fps
        self.note = note
        self.on_seconds = on
        self.off_seconds = off
        self.rounded = rounded
        self.on = self.onf(rounded=rounded)
        self.off = self.offf(rounded=rounded)
        self.duration = self.off - self.on
        self.idx = idx

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


class MidiNoteValue():
    def __init__(self, note, value, svalue, count, index, position, continuation=False):
        self.note = note
        self.value = value
        self.svalue = svalue
        self.count = count
        self.index = index
        self.position = position
        self.continuation = continuation
    
    def __repr__(self):
        return "<MidiNoteValue={:0.3f}({:02d});note:{:04d};count:{:04d};({:04d}/{:04d}):{:b}>".format(self.value, self.position, self.note.note if self.note else -1, self.count, self.note.on if self.note else -1, self.note.off if self.note else -1, self.continuation)
    
    def valid(self):
        return self.note and self.note.note >= 0
    
    def ease(self, eo="eei", ei="eei", negative=False):
        if negative and self.position > 0:
            return -ease(ei, self.value)[0]
        elif self.position > 0:
            return ease(ei, self.value)[0]
        else:
            return ease(eo, self.value)[0]


class MidiTrack():
    def __init__(self, notes, name=None, note_names={}):
        self.notes = sorted(notes, key=lambda n: n.on)
        self.name = name
        self.note_names = note_names
        self.duration = None

    def all_notes(self):
        return set([n.note for n in self.notes])
    
    def fv(self, frame, note_numbers, reverb=[0,5], duration=0, accumulate=0, all=0, monosynth=0):
        pre, post = reverb

        if isinstance(note_numbers, int) or (isinstance(note_numbers, str) and note_numbers != "*"):
            note_numbers = [note_numbers]
        
        if not isinstance(note_numbers, str) and not callable(note_numbers):
            for idx, nn in enumerate(note_numbers):
                note_numbers[idx] = self.note_names.get(nn, 0) if isinstance(nn, str) else nn
        
        if callable(note_numbers):
            note_fn = note_numbers
        elif note_numbers == "*":
            note_fn = lambda n: True
        else:
            note_fn = lambda n: n in note_numbers
        
        count = 0
        notes_on = []
        last_note_off = 0

        for idx, note in enumerate(self.notes):
            if note_fn(note.note) and note.note:
                if monosynth:
                    continuation = note.on <= last_note_off
                else:
                    continuation = False

                note_off = note.off
                if duration > -1:
                    note_off = note.on + duration
                
                if continuation and monosynth:
                    pre_start = note.on
                    post_end = note.off
                else:
                    pre_start = (note.on - pre)
                    post_end = (note_off + post)
                
                note_index = count
                if frame >= pre_start and not continuation: # correct?
                    count += 1
                
                value = 0
                pos = 0
                fi = frame
                
                if frame >= note.on and frame <= note_off: # truly on
                    pos = 0
                    value = 1
                else:
                    if post_end > self.duration and frame < pre_start:
                        fi = frame + self.duration
                    elif pre_start < 0 and frame > post_end:
                        fi = frame - self.duration
                    
                    if fi < note.on and fi >= pre_start:
                        pos = 1
                        value = (fi - pre_start) / pre
                    elif fi > note_off and fi < post_end:
                        pos = -1
                        value = (post_end - fi) / post

                if value > 0:
                    notes_on.append(MidiNoteValue(note, value, -1, count, idx, pos, continuation))
                else:
                    pass
                
                if note.off > last_note_off:
                    last_note_off = note.off

        if accumulate:
            return notes_on
        else:
            if len(notes_on) == 0:
                if monosynth:
                    return None
                else:
                    return MidiNoteValue(note, 0, 0, count, -1, 0)
            else:
                return max(notes_on, key=lambda n: n.value)


class MidiReader():
    def __init__(self, path, duration=None, fps=30, bpm=120, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        midi_path = path if isinstance(path, Path) else Path(path).expanduser()
        mid = mido.MidiFile(str(midi_path))
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
                        events[track.name].append(MidiNote(msg.note, o, cumulative_time, fps, rounded, idx))
                    if msg.type == "note_on" and msg.velocity > 0:
                        open_notes[track.name][msg.note] = cumulative_time

        self.note_names = note_names
        self.midi_file = mid
        self.fps = fps
        self.start = 0
        self.end = 0
        
        tracks = []
        for track_name, es in events.items():
            tracks.append(MidiTrack(es, name=track_name, note_names=note_names_reversed))

        all_notes = []
        for t in tracks:
            for note in t.notes:
                all_notes.append(note)
        
        self.duration = duration or all_notes[-1].off

        for t in tracks:
            t.duration = self.duration
            
        self.min = min([n.note for n in all_notes])
        self.max = max([n.note for n in all_notes])
        self.spread = self.max - self.min
        self.tracks = tracks
    
    def __getitem__(self, item):
        if isinstance(item, str):
            for t in self.tracks:
                if hasattr(t, "name") and t.name == item:
                    return t
        else:
            return self.tracks[item]