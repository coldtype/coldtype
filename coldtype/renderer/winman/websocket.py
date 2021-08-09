import json

from coldtype.renderer.utils import run_echo_server
from coldtype.renderer.config import ColdtypeConfig
from coldtype.renderable import Action

class WinmanWebsocket():
    def __init__(self, config:ColdtypeConfig, renderer):
        self.config = config
        self.renderer = renderer
        
        self.server = run_echo_server(config.websocket_port, "daemon_websocket")


    def send_to_external(self, action, **kwargs):
        animation = self.renderer.animation()
        if animation and animation.timeline:
            #print("EVENT", action, kwargs)
            if action:
                kwargs["action"] = action.value
            kwargs["prefix"] = self.renderer.source_reader.filepath.stem
            kwargs["fps"] = animation.timeline.fps
            for _, client in self.server.connections.items():
                client.sendMessage(json.dumps(kwargs))
    
    def read_messages(self):
        msgs = []
        for _, v in self.server.connections.items():
            if hasattr(v, "messages") and len(v.messages) > 0:
                for msg in v.messages:
                    msgs.append(msg)
                v.messages = []
        
        for msg in msgs:
            self.process_message(msg)
    
    def process_message(self, message):
        try:
            jdata = json.loads(message)
            if "webviewer" in jdata:
                self.renderer.action_waiting = Action.PreviewStoryboard
                return
            
            if "adobe" in jdata:
                print("<coldtype: adobe-panel-connected>")

            action = jdata.get("action")
            if action:
                self.renderer.on_message(jdata, jdata.get("action"))
            elif jdata.get("rendered") is not None:
                idx = jdata.get("rendered")
                self.renderer.state.adjust_keyed_frame_offsets(
                    self.renderer.last_animation.name,
                    lambda i, o: idx)
                self.renderer.action_waiting = Action.PreviewStoryboard
        except:
            self.show_error()
            print("Malformed message")