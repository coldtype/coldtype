import ast, hashlib
from enum import Enum

from coldtype.osutil import on_linux, on_mac, on_windows, System, play_sound

class Watchable(Enum):
    Source = "Source"
    Font = "Font"
    Library = "Library"
    Generic = "Generic"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def bc_print(which, *txt):
    print(f"{which}{' '.join(txt)}{bcolors.ENDC}")


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


def path_hash(path):
    return hashlib.sha1(str(path.resolve()).encode("UTF-8")).hexdigest()[:10]