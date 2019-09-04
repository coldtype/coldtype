from websocket import create_connection
from random import random

import sys, os
dirname = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{dirname}/..")

from coldtype.geometry import Rect

WEBSOCKET_PORT = 8008
WEBSOCKET_ADDR = f"ws://localhost:{WEBSOCKET_PORT}"

class PreviewConnection():
    def __init__(self):
        self.ws = None

    def __enter__(self):
        self.ws = create_connection(WEBSOCKET_ADDR)
        self.ws.send("CLEAR")
        return self

    def __exit__(self, type, value, traceback):
        self.ws.close()
    
    def send(self, content, rect=Rect(0, 0, 500, 500), full=False, image=False):
        if full:
            html = content
        elif image:
            html = f"""<div class="page" style="width:{rect.w}px;height:{rect.h}px"><img style='background:white' src='file:///{content}?q={random()}' width={rect.w}/></div>"""
        else:
            html = f"""<div class="page" style="width:{rect.w}px;height:{rect.h}px">{content}</div>"""
        self.ws.send(html)


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
