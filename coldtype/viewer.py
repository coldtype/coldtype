#!/usr/bin/env python

from websocket import create_connection, WebSocket
from random import random

import sys, os
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/..")

from coldtype.geometry import Rect
from coldtype.color import normalize_color


WEBSOCKET_PORT = 8008
WEBSOCKET_ADDR = f"ws://localhost:{WEBSOCKET_PORT}"


class PersistentPreview():
    def __init__(self):
        self.ws = create_connection(WEBSOCKET_ADDR)
    
    def clear(self):
        self.ws.send("CLEAR")
    
    def close(self):
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

        norm_bg = normalize_color(bg)
        rgba = f"rgba({round(norm_bg.red*255)}, {round(norm_bg.green*255)}, {round(norm_bg.blue*255)}, {norm_bg.alpha})"
        
        def wrap(content):
            if rect:
                w = rect.w
                h = rect.h
                if max_width < w:
                    w = max_width
                    h = rect.h * (max_width / rect.w)
                return f"""
                <div class="page" style="width:{w}px;height:{h}px;background:{rgba};">{content}</div>\
                """
            else:
                return f"""
                <div class="plain" style="background:{rgba};">{content}</div>
                """
        
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


class PreviewConnection():
    def __init__(self):
        self.pp = None

    def __enter__(self):
        self.pp = PersistentPreview()
        self.pp.clear()
        return self

    def __exit__(self, type, value, traceback):
        self.pp.close()
    
    def send(self, *args, **kwargs):
        self.pp.send(*args, **kwargs)



def previewer():
    return PreviewConnection()

def viewer():
    return PreviewConnection()


if __name__ == "__main__":
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

    clients = []

    class SimpleChat(WebSocket):
        def handleMessage(self):
            for client in clients:
                if client != self:
                    # self.address[0]
                    client.sendMessage(self.data)

        def handleConnected(self):
            print(self.address, 'connected')
            clients.append(self)

        def handleClose(self):
            clients.remove(self)
            print(self.address, 'closed')


    server = SimpleWebSocketServer('', WEBSOCKET_PORT, SimpleChat)
    print(">>> Listening on", WEBSOCKET_PORT)
    server.serveforever()
