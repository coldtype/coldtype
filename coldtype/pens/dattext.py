from coldtype.pens.datpen import DATPen


class DATText(DATPen):
    def __init__(self, text, style, frame):
        self.text = text
        self.style = style
        self.visible = True
        super().__init__()
        self.addFrame(frame)
    
    def __str__(self):
        return f"<DT({self.text}/{self.style.font})/>"