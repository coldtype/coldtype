from coldtype.renderer.config import ColdtypeConfig
from coldtype.renderer.winman.passthrough import WinmanPassthrough
from coldtype.renderer.winman.glfwskia import glfw, skia, WinmanGLFWSkia, WinmanGLFWSkiaBackground
from coldtype.renderer.winman.webview import WinmanWebview


class Winmans():
    def __init__(self, renderer, config:ColdtypeConfig):
        self.config = config

        self.pt = WinmanPassthrough()
        self.glsk = None
        self.wv = None
        self.b3d = None

    def should_glfwskia(self):
        return glfw is not None and skia is not None and not self.config.no_viewer
    
    def all(self):
        return [self.pt, self.glsk, self.wv, self.b3d]
    
    def map(self):
        for wm in self.all():
            if wm:
                yield wm
    
    def set_title(self, text):
        [wm.set_title(text) for wm in self.map()]
    
    def reset(self):
        [wm.reset() for wm in self.map()]
    
    def terminate(self):
        [wm.terminate() for wm in self.map()]