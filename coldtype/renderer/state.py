from pathlib import Path
import json


class RendererStateEncoder(json.JSONEncoder):
    def default(self, o):
        return {
            "controller_values": o.controller_values
        }


class RendererState():
    def __init__(self, renderer):
        self.renderer = renderer
        self.controller_values = {}
        self.reset()
    
    def reset(self):
        if fp := self.filepath:
            try:
                deserial = json.loads(fp.read_text())
                if cv := deserial.get("controller_values"):
                    self.controller_values = cv
            except json.decoder.JSONDecodeError:
                self.controller_values = {}
            except FileNotFoundError:
                self.controller_values = {}
    
    def clear(self):
        if fp := self.filepath:
            fp.write_text("")
        self.reset()
    
    @property
    def filepath(self):
        if fp := self.renderer.filepath:
            return Path(str(fp).replace(".py", "") + "_state.json")
        else:
            return None
    
    @property
    def midi(self):
        return self.controller_values
    
    def persist(self):
        if fp := self.filepath:
            print("Saving Controller State...")
            fp.write_text(RendererStateEncoder().encode(self))
        else:
            print("No source; cannot persist state")