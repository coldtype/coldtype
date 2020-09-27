class RendererState():
    def __init__(self):
        self.controller_values = {}
    
    @property
    def midi(self):
        return self.controller_values