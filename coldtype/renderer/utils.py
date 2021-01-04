import sys, os
import ast, threading

from enum import Enum
from pathlib import Path

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

WEBSOCKET_PORT = 8007

class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"
    Generic = "Generic"
    

class EditAction(Enum):
    Newline = "newline"
    Tokenize = "tokenize"
    TokenizeLine = "tokenize_line"
    NewSection = "newsection"
    Capitalize = "capitalize"
    SelectWorkarea = "select_workarea"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SimpleEcho(WebSocket):
    def handleMessage(self):
        #print("INCOMING", self, self.data)
        self.messages.append(self.data)

    def handleConnected(self):
        print(self.address, 'connected')
        self.messages = []

    def handleClose(self):
        print(self.address, 'closed')


def echo_server():
    return SimpleWebSocketServer('', WEBSOCKET_PORT, SimpleEcho)


def bytesto(bytes):
    r = float(bytes)
    for i in range(2):
        r = r / 1024
    return(r)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def file_and_line_to_def(filepath, lineno):
    # https://julien.danjou.info/finding-definitions-from-a-source-file-and-a-line-number-in-python/
    candidate = None
    for item in ast.walk(ast.parse(filepath.read_text())):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if item.lineno > lineno:
                continue
            if candidate:
                distance = lineno - item.lineno
                if distance < (lineno - candidate.lineno):
                    candidate = item
            else:
                candidate = item
    if candidate:
        return candidate.name