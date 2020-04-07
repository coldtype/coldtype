import json
from random import random
from websocket import create_connection, WebSocket
from coldtype.geometry import Rect
from coldtype.color import normalize_color


WEBSOCKET_PORT = 8007
WEBSOCKET_ADDR = f"ws://localhost:{WEBSOCKET_PORT}"


class PersistentPreview():
    def __init__(self):
        try:
            self.ws = create_connection(WEBSOCKET_ADDR)
        except:
            self.ws = None
    
    def clear(self):
        if self.ws:
            self.ws.send(json.dumps(dict(clear=True)))
    
    def close(self):
        if self.ws:
            self.ws.close()
    
    def send(self,
             content,
             rect=None,
             full=False,
             image=False,
             pdf=False,
             bg=(1, 1, 1, 0),
             max_width=5000
        ):
        if not self.ws:
            print(content)
            return

        norm_bg = normalize_color(bg)
        rgba = f"rgba({round(norm_bg.r*255)}, {round(norm_bg.g*255)}, {round(norm_bg.b*255)}, {norm_bg.a})"
        
        def wrap(content):
            if rect:
                w = rect.w
                h = rect.h
                if max_width < w:
                    w = max_width
                    h = rect.h * (max_width / rect.w)
                html = f"""
                <div class="page" style="width:{w}px;height:{h}px;background:{rgba};">{content}</div>\
                """
            else:
                html = f"""
                <div class="plain" style="background:{rgba};">{content}</div>
                """
            return json.dumps(dict(html=html))
        
        if full:
            html = content
        elif image:
            if isinstance(content, str):
                images = [content]
            else:
                images = content
            imgs = ""
            for img in images:
                imgs += f"""<img style='position:absolute;top:0px;left:0px;' src='file:///{img}?q={random()}' width={rect.w}/>"""
            html = wrap(imgs)
        elif pdf:
            if isinstance(content, str):
                pdfs = [content]
            else:
                pdfs = content
            pdf_html = ""
            for pdf in pdfs:
                pdf_html += f"""<iframe style='position:absolute;top:0px;left:0px;' src='file:///{pdf}?q={random()}' width="{rect.w}" height="{rect.h}"/>"""
            html = wrap(pdf_html)
        else:
            html = wrap(content)
        self.ws.send(html)
