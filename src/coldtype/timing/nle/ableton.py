from coldtype.timing import Timeline, Timeable
from coldtype.helpers import sibling

from pathlib import Path
from functools import partial
from lxml import etree
import gzip, math

import xml.dom.minidom as mini
import xml.etree.ElementTree as ET

# DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip/Notes/KeyTracks

def save_test_xml(x):
    sibling(__file__, "test_read_ableton.xml").write_text(etree.tostring(x, pretty_print=True).decode())


def b2f(fpb, t):
    return math.floor(t * fpb)


def b2ms(bpm, b):
    return b * (60000 / bpm)


def midi_to_note_name(midi_number):
    if not (0 <= midi_number <= 127):
        return "Invalid MIDI note number"

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_index = midi_number % 12
    octave = (midi_number // 12) - 2

    note_name = note_names[note_index]
    return f"{note_name}{octave}"


def note_name_to_midi(note_name):
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    note = note_name[:-1]
    octave = int(note_name[-1])
    
    if note not in note_names:
        return "Invalid note name"
    
    note_index = note_names.index(note)
    midi_number = (octave + 2) * 12 + note_index
    
    if not (0 <= midi_number <= 127):
        return "MIDI number out of range"
    
    return midi_number


strings = {
    "D4": 1, "F4": 1, "G4": 1,
    "C4": 2,
    "G3": 3, "G#3": 3, "A3": 3, "B3": 3,
    "C3": 4, "D3": 4, "E3": 4, "F3": 4,
    "C2": 0,
}

def string_and_note_to_fret(string, note):
    return {
        0: {
            "C2": 0,
        },
        1: {
            "D4": 0, "D#4": 1, "E4": 2, "F4": 3, "F#4": 4,"G4": 5,
        },
        2: {
            "C4": 0, "C#4": 1, "D4": 2, "E4": 4,
        },
        3: {
            "G3": 0, "G#3": 1, "A3": 2, "A#3": 3, "B3": 4, "C4": 5,
        },
        4: {
            "C3": 0, "C#3": 1, "D3": 2, "D#3": 3, "E3": 4, "F3": 5
        }
    }[string][note]


class AbletonMIDINote(Timeable):
    def __repr__(self):
        return f"<AbletonMIDINote {self.name},{self.start},{self.end}/>"


class AbletonMIDIClip(Timeline):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])

        timeables_by_id = dict()

        super().__init__(name=clip_name, findWords=False, start=b2ff(clip_start), end=b2ff(clip_end))

        for idx, kt in enumerate(clip.findall("Notes/KeyTracks/KeyTrack")):
            midi_key = kt.find("MidiKey").attrib["Value"]
            for jdx, note in enumerate(kt.find("Notes")):
                na = dict(note.attrib).copy()
                #if na["IsEnabled"]:
                nt = clip_start + float(na["Time"])
                nd = float(na["Duration"])
                note_id = na["NoteId"]
                vel = float(na["Velocity"])
                note_name = midi_to_note_name(int(midi_key))
                
                string = strings.get(note_name, None)
                if string is None:
                    string = 0

                fret = string_and_note_to_fret(string, note_name)
                end = b2ff(nt+nd)
                if note_name == "G4" and vel < 100:
                    end = b2ff(nt+nd+0.25)
                    string = 5
                    fret = 0
                note = AbletonMIDINote(b2ff(nt), end, jdx, midi_key, id=note_id, data=dict(velocity=vel, note=note_name, string=string, fret=fret))
                self.timeables.append(note)
                timeables_by_id[note_id] = note
        
        for idx, el in enumerate(clip.findall("Notes/PerNoteEventStore/EventLists/PerNoteEventList")):
            note_id = el.attrib["NoteId"]
            note = timeables_by_id[note_id]
            cc = el.attrib["CC"]
            if cc == "-2":
                adjusted_negatives = False
                string = note.data.get("string")
                start_note = int(note.name)
                start_note_name = midi_to_note_name(start_note)

                for jdx, event in enumerate(el.find("Events")):
                    offset = float(event.attrib["TimeOffset"])
                    value = float(event.attrib["Value"])
                    
                    if offset < 0.01 and abs(value) > 1:
                        note.data["hammer"] = True
                        continue
                    
                    if value < 0.01 and not adjusted_negatives: # pull-offs, always?
                        if start_note_name == "D4":
                            adjusted_negatives = True
                            string = string + 1
                            note.data["string"] = string
                            note.data["fret"] = 2

                    note_diff = value / 170
                    new_note = int(start_note) + round(note_diff)
                    new_note_name = midi_to_note_name(new_note)
                    #print(midi_to_note_name(start_note), string, new_note_name, value)

                    note.timeables.append(Timeable(b2ff(offset), b2ff(offset)+1, jdx, str(new_note)
                        , data=dict(value=value
                            , note=new_note_name
                            , string=string
                            , fret=string_and_note_to_fret(string, new_note_name)
                            )))


class AbletonMIDITrack(Timeline):
    def __init__(self, b2ff, track):
        self.b2ff = b2ff
        
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        if track_name == "banjo":
            timeables = [AbletonMIDIClip(b2ff, clip) for clip in track.findall("DeviceChain/MainSequencer/ClipTimeable/ArrangerAutomation/Events/MidiClip")]
        else:
            timeables = []
        
        super().__init__(timeables=timeables, findWords=False, name=track_name)

        automation = []
        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)

        self.xml = track
        self.automation = automation

    def notes(self):
        return [int(t.name) for t in self.flat_timeables()]
    
    def range(self):
        ns = self.notes()
        return min(ns), max(ns)


class AbletonAudioClip(Timeable):
    def __init__(self, b2ff, clip):
        clip_name = clip.find("Name").attrib["Value"]
        clip_start = float(clip.find("CurrentStart").attrib["Value"])
        clip_end = float(clip.find("CurrentEnd").attrib["Value"])

        super().__init__(b2ff(clip_start), b2ff(clip_end), name=clip_name)


class AbletonAudioTrack(Timeline):
    def __init__(self, b2ff, track):
        self.lx = track
        track_name = track.find("Name/EffectiveName").attrib["Value"]
        clips = []
        for clip in track.findall("DeviceChain/MainSequencer/Sample/ArrangerAutomation/Events/AudioClip"):
            clips.append(AbletonAudioClip(b2ff, clip))

        automation = []
        for a in track.xpath("AutomationEnvelopes/Envelopes/AutomationEnvelope/Automation"):
            automation.append(a)
        self.automation = automation

        super().__init__(timeables=clips, findWords=False, name=track_name)
        #super().__init__(clips, name=track_name)


class AbletonReader(Timeline):
    def __init__(self, path, duration=-1, fps=30, rounded=True, note_names={}):
        note_names_reversed = {v:k for (k,v) in note_names.items()}
        als_path = path if isinstance(path, Path) else Path(path).expanduser()

        lx = None
        if als_path.suffix == ".xml":
            with open(str(als_path), "rb") as f:
                lx = etree.fromstring(f.read())
        else:
            with gzip.open(str(als_path), "rb") as f:
                lx = etree.fromstring(f.read())
        
        self.lx = lx

        master_track = lx.find("LiveSet/MainTrack")
        bpm = float(master_track.find("AutomationEnvelopes/Envelopes/AutomationEnvelope[@Id='1']/Automation/Events/FloatEvent").attrib["Value"])

        fpb = (60/bpm)*fps
        b2ff = partial(b2f, fpb)
        self.b2ff = b2ff

        self.returns = []

        tracks = []
        for t in lx.xpath("LiveSet/Tracks/*"):
            if t.tag == "MidiTrack":
                tracks.append(AbletonMIDITrack(b2ff, t))
            elif t.tag == "AudioTrack":
                #tracks.append(AbletonAudioTrack(b2ff, t))
                pass
            elif t.tag == "ReturnTrack":
                self.returns.append(t)
        
        if duration == -1:
            duration = max([t.end for t in tracks])
        
        # huh?
        #for t in tracks:
        #    t.constrain(0, duration)

        super().__init__(duration=duration, fps=fps, timeables=tracks, findWords=False, name="Ableton")
        #super().__init__(duration, fps=fps, tracks=tracks)

if __name__ == "<run_path>":
    from coldtype import *
    
    ar = AbletonReader("~/Waves/projs/2024.02.05.1 Project/__silentnighttab3.als")

    #print(ar.timeables[0].timeables[0].timeables)
    
    # el = ar.timeables[1].automation[0]
    # points = {}
    # for fe in el.findall("Events/FloatEvent"):
    #     b = float(fe.attrib["Time"])
    #     frame = ar.b2ff(b)
    #     percent = float(fe.attrib["Value"])
    #     fr = b2f((60/120)*30, b)
    #     if fr < 0:
    #         fr = 0
    #     points[fr] = percent
    
    # interp = []
    # for fr in range(0, ar.duration):
    #     p = points.get(fr, None)
    #     if p:
    #         interp.append(p)
    #     else:
    #         pass

    #reparsed = mini.parseString(ET.tostring(el, 'utf-8'))
    #print(reparsed.toprettyxml(indent="  "))

    colors = {
        0: bw(1),
        1: hsl(0.3, 0.60, 0.6),
        2: hsl(0.6, 0.7, 0.65),
        3: hsl(0.9, 0.7, 0.5),
        4: hsl(0.6, 0.90, 0.58),
        5: hsl(0.9, 0.7, 0.6),
    }

    string_names = {
        0: "X",
        1: "D",
        2: "C",
        3: "G",
        4: "C",
        5: "g",
    }

    string_notes = {
        "D4": 1,
        "C4": 2,
        "G3": 3,
        "C3": 4,
        "G4": 5,
        "C2": 0,
    }

    @animation(Rect(1920*2-400, 1080), tl=ar, bg=0)
    def ableton(f):
        xs = 4
        ys = 32
        
        notes = P()
        hits = P()
        frets = P()
        bars = P()

        g = 1725
        
        for t in ar.timeables[0].timeables[0].timeables:
            n:AbletonMIDINote = t
            note = n.data.get("note")
            fret = str(n.data.get("fret"))
            string = n.data.get("string")
            vel = n.data.get("velocity")
            color = colors.get(string, 1)
            x = n.start*xs
            y = int(n.name)*ys

            def add_fret(_fret, x, y):
                frets.append(StSt(_fret, "MDIO-VF", 32, wght=0.65).t(x-9, y+33).f(0)
                    .pen().up().insert(0, lambda p: P().oval(p.ambit(tx=0, ty=0).inset(-9))
                        .f(color.lighter(0.2).with_alpha(0.75))))

            if note == "C2":
                y = 1620
                bars.append(P().line([Point(x, y).o(0, -2), Point(x, y).o(0, 1000)]).fssw(-1, bw(1, min(0.35, vel/127)), 2))
                continue

            show_note = True
            if string == 5:
                show_note = False
                y = g
            
            bend_points = [Point(x, y+ys/2)]
            last_y = y+ys/2
            last_fret = fret

            for b in n.timeables:
                #if b.start < 0.01:
                #    continue
                _x = x + b.start*xs
                _y = y+ys/2+(b.data["value"]/170)*ys
                p = Point(_x, _y)
                last_y = p.y
                bend_points.append(p)
                bend_fret = str(b.data.get("fret"))
                if b.start > 0.01 and last_fret != bend_fret:
                    last_fret = bend_fret
                    if bend_fret != "0":
                        add_fret(bend_fret, _x, _y-12)
                        # frets.append(StSt(bend_fret, "MDIO-VF", 32, wght=0.65).t(_x-9, _y+10).f(1)
                        #     .pen().up().insert(0, lambda p: P().oval(p.ambit(tx=0, ty=0).inset(-9)).f(color.darker(0.2))))
                        # #frets.append(StSt(bend_fret, "MDIO-VF", 32, wght=0.65).t(_x-9, _y+10).f(color))
            
            bend_points.append(Point(x+n.duration*xs, last_y))
            notes.append(P().line(bend_points).f(color).outline(5, cap="butt").ro())
            
            if n.data.get("hammer"):
                hits.append(P().line([Point(x, y).o(0, -2).o(14, 0), Point(x, y).o(0, -2), Point(x, y).o(0, ys+2), Point(x, y).o(0, ys+2).o(14, 0)]).fssw(-1, hsl(0.17, 0.6, 0.8), 2))
            else:
                hits.append(P().line([Point(x, y).o(0, -2), Point(x, y).o(0, ys+2)]).fssw(-1, 1, 2))

            if show_note and fret != "0":
                add_fret(fret, x, y)
        
        opens = P()
        last_string = None

        for x in range(note_name_to_midi("C3"), note_name_to_midi("G4")+2):
            note = midi_to_note_name(x)
            if "#" not in note:
                y = x*ys+ys/2

                if note in string_notes:
                    string = string_notes[note]
                    if note != "G4":
                        last_string = string
                    _y = y
                    if string == 5:
                        _y = g + ys/2
                    opens.append(P(
                        P().line([Point(-100, _y), Point(notes.ambit().mxx + 100, _y)])
                            .fssw(-1, colors[string].with_alpha(0.65), 3),
                        StSt(string_names[string], "MDIO-VF", 66, wght=0.75).t(-180, _y-16).f(colors[string])))
                
                if note not in string_notes or note == "G4":
                    color = bw(1)
                    opens.append(P(
                        P().line([Point(-100, y), Point(notes.ambit().mxx + 100, y)])
                            .fssw(-1, colors[last_string].with_alpha(0.65), 1),
                        StSt(note[0], "MDIO-VF", 32, wght=0.25).t(-126, y-9).f(colors[last_string])))

        return P(bars, opens, notes, hits, frets).scale(0.75).align(f.a.r.inset(60), "W")

        #e1 = ar.timeables[1].timeables[0].ki(60, f.i).adsr([7, 0, 0, 30])
        #e2 = ar.timeables[1].timeables[0].ki(65, f.i).adsr([7, 0, 0, 30])
        #return (P(
        #    P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.017, 0.8, 0.7), 3).scale(e1+0.25),
        #    P().oval(f.a.r.inset(100)).fssw(-1, hsl(0.7, 0.8, 0.7), 3).scale(e2+0.2),
        #))