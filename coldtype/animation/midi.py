import mido, math
from pathlib import Path

from coldtype.animation.timeline import Timeline
from coldtype.animation.easing import ease


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


class MidiNoteValue():
    def __init__(self, note, value, svalue, count, index):
        self.note = note
        self.value = value
        self.svalue = svalue
        self.count = count
        self.index = index
    
    def __repr__(self):
        return "<MidiNoteValue={:0.3f}/{:0.3f};note:{:04d};count:{:04d}>".format(self.value, self.svalue, self.note.note if self.note else -1, self.count)
    
    def valid(self):
        return self.note and self.note.note >= 0
    
    def ease(self, eo="eei", ei="eei"):
        return ease(eo, self.value)[0]


class MidiTrack():
    def __init__(self, notes, name=None, note_names={}):
        self.notes = sorted(notes, key=lambda n: n.on)
        self.name = name
        self.note_names = note_names

    def all_notes(self):
        return set([n.note for n in self.notes])
    
    def fv(self, frame, note_numbers, reverb=[0,0], accumulate=0, all=0):
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
        note_indices = []

        for idx, note in enumerate(self.notes):
            if note.on-pre > frame:
                continue
            elif note_fn(note.note):
                if frame >= (note.on-pre):
                    count += 1
                if frame >= (note.on-pre) and frame < (note.off+post):
                    notes_on.append(note)
                    note_indices.append(idx)
        
        if len(notes_on) > 0:
            values = []
            svalues = []
            for note in notes_on:
                v = 1 - ((frame - note.on) / (note.duration+post))
                if frame > note.off:
                    if post > 0:
                        sv = 1 - ((frame - note.off) / post)
                    else:
                        sv = 0
                else:
                    sv = 1
                if v > 1:
                    v = 2 + ((frame - note.on - pre) / pre)
                    sv = v
                values.append(v)
                svalues.append(sv)
            if accumulate:
                all_values = []
                for i, note in enumerate(notes_on):
                    all_values.append(MidiNoteValue(note, values[i], svalues[i], 1, note_indices[i]))
                return all_values
            else:
                return MidiNoteValue(notes_on[-1], max(values), max(svalues), count, note_indices[-1])
        else:
            if accumulate:
                return []
            else:
                return MidiNoteValue(None, 0, 0, count, -1)


class MidiReader():
    def __init__(self, path, fps=30, bpm=120, rounded=True, note_names={}):
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
                        events[track.name].append(MidiNote(msg.note, o, cumulative_time, fps, rounded))
                    if msg.type == "note_on" and msg.velocity > 0:
                        open_notes[track.name][msg.note] = cumulative_time
        tracks = []
        for track_name, es in events.items():
            tracks.append(MidiTrack(es, name=track_name, note_names=note_names_reversed))

        all_notes = []
        for t in tracks:
            for note in t.notes:
                all_notes.append(note)
        
        self.note_names = note_names
        self.min = min([n.note for n in all_notes])
        self.max = max([n.note for n in all_notes])
        self.spread = self.max - self.min
        self.midi_file = mid
        self.fps = fps
        self.tracks = tracks
        self.start = 0
        self.end = 0
        self.duration = all_notes[-1].off
    
    def __getitem__(self, item):
        if isinstance(item, str):
            for t in self.tracks:
                if hasattr(t, "name") and t.name == item:
                    return t
        else:
            return self.tracks[item]