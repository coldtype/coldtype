
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
        self.failed = False
        self.devices = []

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
            self.failed = True
            print("MIDI SETUP EXCEPTION >", e)
    
    def monitor(self, playing):
        if self.failed:
            return

        controllers = {}
        shortcut_triggered = False

        for device, mi in self.devices:
            msg = mi.getMessage(0)
            while msg:
                if self.config.midi_info:
                    print(device, msg)
                
                if msg.isNoteOn(): # Maybe not forever?
                    nn = msg.getNoteNumber()
                    shortcut = self.config.midi[device]["note_on"].get(nn)
                    if shortcut:
                        self.on_shortcut(shortcut, nn)
                        shortcut_triggered = True
                elif msg.isNoteOff():
                    nn = msg.getNoteNumber()
                elif msg.isController():
                    cn = msg.getControllerNumber()
                    cv = msg.getControllerValue()
                    cc = msg.getChannel()
                    
                    mapping = self.config.midi[device].get("controller", {})
                    shortcutA = mapping.get(cn)
                    shortcutB = mapping.get((cn, cc))
                    
                    if shortcutA:
                        if cv in shortcutA:
                            print("shortcut!", shortcutA, cv, shortcutA.get(cv))
                            self.on_shortcut(shortcutA.get(cv), cn)
                            shortcut_triggered = True
                    
                    if shortcutB:
                        if callable(shortcutB):
                            res = shortcutB(cv, self.state)
                            if res is not None:
                                print("shortcut!", res)
                                self.on_shortcut(res, None)
                                shortcut_triggered = True
                        else:
                            if cv in shortcutB:
                                print("shortcut!", shortcutB, cv)
                                self.on_shortcut(shortcutB.get(cv), cn)
                                shortcut_triggered = True
                    
                    else:
                        controllers["_".join([device, str(cc), str(cn)])] = cv
                
                msg = mi.getMessage(0)
        
        if len(controllers) > 0:
            nested = {}
            for k, v in controllers.items():
                device, channel, number = k.split("_")
                if not nested.get(device):
                    nested[device] = {}
                if not nested[device].get(channel):
                    nested[device][channel] = {}
                nested[device][channel][str(number)] = v
            
            for device, channels in nested.items():
                if not self.state.controller_values.get(device):
                    self.state.controller_values[device] = {}
                for channel, numbers in channels.items():
                    if not self.state.controller_values[device].get(channel):
                        self.state.controller_values[device][channel] = {}
                    for number, value in numbers.items():
                        was = self.state.controller_values[device][channel].get(number)
                        if was:
                            self.state.controller_values[device][channel]["_" + str(number)] = was
                        self.state.controller_values[device][channel][number] = value

            if not playing and not shortcut_triggered:
               return True