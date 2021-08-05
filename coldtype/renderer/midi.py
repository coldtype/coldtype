
try:
    import rtmidi
except ImportError:
    rtmidi = None
    pass

class MIDIWatcher():
    def __init__(self, config, state, on_shortcut):
        self.config = config
        self.state = state
        self.on_shortcut = on_shortcut
        self.devices = []
        self.no_midi = self.config.no_midi

        if self.no_midi:
            return

        if self.config.midi_info and not rtmidi:
            print("Please run `pip install rtmidi` in your venv")
            self.no_midi = True

        if rtmidi and not self.no_midi:
            try:
                midiin = rtmidi.RtMidiIn()
                lookup = {}
                for p in range(midiin.getPortCount()):
                    lookup[midiin.getPortName(p)] = p

                for device, mapping in self.config.midi.items():
                    if device in lookup:
                        mapping["port"] = lookup[device]
                        mi = rtmidi.RtMidiIn()
                        mi.openPort(lookup[device])
                        self.devices.append([device, mi])
                    else:
                        if self.config.midi_info:
                            print(f">>> no midi port found with that name ({device}) <<<")
                
                if self.config.midi_info:
                    print("\nMIDI DEVICES:::")
                    midiin = rtmidi.RtMidiIn()
                    ports = range(midiin.getPortCount())
                    for p in ports:
                        print(">", f"\"{midiin.getPortName(p)}\"")
                    print("\n")

            except Exception as e:
                print("MIDI SETUP EXCEPTION >", e)
    
    def monitor(self, playing):
        if self.no_midi:
            return

        controllers = {}
        for device, mi in self.devices:
            msg = mi.getMessage(0)
            while msg:
                if self.config.midi_info:
                    print(device, msg)
                if msg.isNoteOn(): # Maybe not forever?
                    nn = msg.getNoteNumber()
                    shortcut = self.config.midi[device]["note_on"].get(nn)
                    self.on_shortcut(shortcut, nn)
                if msg.isController():
                    cn = msg.getControllerNumber()
                    cv = msg.getControllerValue()
                    shortcut = self.config.midi[device].get("controller", {}).get(cn)
                    if shortcut:
                        if cv in shortcut:
                            print("shortcut!", shortcut, cv)
                            self.on_shortcut(shortcut.get(cv), cn)
                    else:
                        controllers[device + "_" + str(cn)] = cv/127
                msg = mi.getMessage(0)
        
        if len(controllers) > 0:
            nested = {}
            for k, v in controllers.items():
                device, number = k.split("_")
                if not nested.get(device):
                    nested[device] = {}
                nested[device][str(number)] = v
            
            for device, numbers in nested.items():
                self.state.controller_values[device] = {**self.state.controller_values.get(device, {}), **numbers}

            if not playing:
                return True