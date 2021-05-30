import ast, json
from http.server import SimpleHTTPRequestHandler
from enum import Enum

try:
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
except ImportError:
    SimpleWebSocketServer = object
    WebSocket = object


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
        if "webviewer" in self.data:
            data = json.loads(self.data)
            if data.get("webviewer") == True:
                self.webviewer = True
        #print("INCOMING!", self, self.address, self.data)
        self.messages.append(self.data)

    def handleConnected(self):
        #if not str(self.address).startswith("('::ffff"):
        #    print(self.address, "connected")
        self.messages = []
        self.webviewer = False

    def handleClose(self):
        #print(self.address, "closed")
        pass


def echo_server(port):
    return SimpleWebSocketServer('', port, SimpleEcho)


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