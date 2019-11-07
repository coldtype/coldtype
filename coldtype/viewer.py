from websocket import create_connection, WebSocket
from random import random

import sys, os
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/..")

from coldtype.geometry import Rect
from coldtype.color import normalize_color


WEBSOCKET_PORT = 8008
WEBSOCKET_ADDR = f"ws://localhost:{WEBSOCKET_PORT}"


def send(ws, content, rect=Rect(0, 0, 500, 500), full=False, image=False, pdf=False, bg=(0, 0, 0, 0)):
    bg = normalize_color(bg).html
    if full:
        html = content
    elif image:
        if isinstance(content, str):
            images = [content]
        else:
            images = content
        imgs = ""
        for img in images:
            imgs += f"""<img style='background:{bg};position:absolute;top:0px;left:0px;' src='file:///{img}?q={random()}' width={rect.w}/>"""
        html = f"""<div class="page" style="position:relative;width:{rect.w}px;height:{rect.h}px">{imgs}</div>"""
    elif pdf:
        if isinstance(content, str):
            pdfs = [content]
        else:
            pdfs = content
        pdf_html = ""
        for pdf in pdfs:
            pdf_html += f"""<iframe style='background:{bg};position:absolute;top:0px;left:0px;' src='file:///{pdf}?q={random()}' width="{rect.w}" height="{rect.h}"/>"""
        html = f"""<div class="page" style="position:relative;width:{rect.w}px;height:{rect.h}px">{pdf_html}</div>"""
    else:
        html = f"""<div class="page" style="width:{rect.w}px;height:{rect.h}px;background:{bg}">{content}</div>"""
    ws.send(html)


class PersistentPreview():
    def __init__(self, receiver=None):
        self.ws = create_connection(WEBSOCKET_ADDR, class_=receiver)
    
    def clear(self):
        self.ws.send("CLEAR")
    
    def send(self, content, rect=Rect(0, 0, 500, 500), full=False, image=False, pdf=False, bg=(0, 0, 0, 0)):
        send(self.ws, content, rect=rect, full=full, image=image, pdf=pdf, bg=bg)
    
    def close(self):
        self.ws.close()


class PreviewConnection():
    def __init__(self):
        self.ws = None

    def __enter__(self):
        self.ws = create_connection(WEBSOCKET_ADDR)
        self.ws.send("CLEAR")
        return self

    def __exit__(self, type, value, traceback):
        self.ws.close()
    
    def send(self, content, rect=Rect(0, 0, 500, 500), full=False, image=False, pdf=False, bg=(0, 0, 0, 0)):
        send(self.ws, content, rect=rect, full=full, image=image, pdf=pdf, bg=bg)



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
