import sys, os
import ast, threading

from enum import Enum
from pathlib import Path

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from http.server import BaseHTTPRequestHandler, HTTPServer

WEBSOCKET_PORT = 8007
HTTP_PORT = 8008

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


class LoggingServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print("GET", self.path, self.headers)
        self._set_response()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print("POST", self.path, self.headers, post_data.encode("utf-8"))
        self._set_response()


def http_server(server_class=HTTPServer, handler_class=LoggingServer, port=HTTP_PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


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