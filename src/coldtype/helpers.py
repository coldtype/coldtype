from pathlib import Path
from coldtype.text.reader import normalize_font_path
from coldtype.interpolation import norm, interp_dict, lerp, loopidx
from coldtype.random import random_series

try:
    from defcon import Font as DefconFont
except ImportError:
    DefconFont = None


def sibling(root, file):
    return Path(root).parent.joinpath(file)

def download(url, save_to:Path, force=False):
    import requests

    if not force and save_to.exists():
        return save_to

    save_to.parent.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(url)
    response.raise_for_status()
    
    with save_to.open("wb") as f:
        f.write(response.content)
    
    return save_to

def raw_ufo(path):
    return DefconFont(normalize_font_path(path))

def quick_ufo(path
    , familyName
    , styleName="Regular"
    , versionMajor=1
    , versionMinor=0
    , unitsPerEm=1000
    , descender=-250
    , ascender=750
    , capHeight=750
    , xHeight=500
    ):
    np:Path = Path(path).expanduser().resolve()
    
    if not np.exists():
        np.parent.mkdir(exist_ok=True, parents=True)
        ufo = DefconFont()
        ufo.save(str(np))
    
    ufo = DefconFont(str(np))

    ufo.info.familyName = familyName
    ufo.info.styleName = styleName
    ufo.info.versionMajor = versionMajor
    ufo.info.versionMinor = versionMinor
    ufo.info.unitsPerEm = unitsPerEm
    ufo.info.descender = descender
    ufo.info.xHeight = xHeight
    ufo.info.capHeight = capHeight
    ufo.info.ascender = ascender

    return ufo


def ßhide(el):
    return None

def ßshow(el):
    return el

def cycle_idx(arr, idx):
    if idx < 0:
        return len(arr) - 1
    elif idx >= len(arr):
        return 0
    else:
        return idx

_by_uni = None
_by_glyph = None
_class_lookup = None

def _populate_glyphs_unis():
    global _by_uni
    global _by_glyph
    global _class_lookup
    _by_uni = {}
    _by_glyph = {}
    _class_lookup = {}

    #try:
    if True:
        lines = (Path(__file__).parent / "assets/glyphNamesToUnicode.txt").read_text().split("\n")

        for l in lines:
            if l.startswith("#"):
                continue
            l = l.split(" ")[:3]
            uni = int(l[1], 16)
            _by_uni[uni] = l[0]
            _by_glyph[l[0]] = uni
            _class_lookup[l[0]] = l[2]
    #except:
    #    pass

def uni_to_glyph(u):
    if not _by_uni:
        _populate_glyphs_unis()
    return _by_uni.get(u)
    
def glyph_to_uni(g):
    if g.lower() in [
        "gcommaaccent",
        "kcommaaccent",
        "lcommaaccent",
        "ncommaaccent",
        "rcommaaccent",
        ]:
        g = g.replace("commaaccent", "cedilla")
    elif g.lower() == "kgreenlandic":
        g = g.replace("greenlandic", "ra")
    if not _by_glyph:
        _populate_glyphs_unis()
    return _by_glyph.get(g)

def glyph_to_class(g):
    if not _class_lookup:
        _populate_glyphs_unis()
    return _class_lookup.get(g)

# Function for running async code synchronously from both standard sync code and from a notebook context

#https://stackoverflow.com/questions/55647753/call-async-function-from-sync-function-while-the-synchronous-function-continues

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine, TypeVar

__all__ = [
    "run_coroutine_sync",
]

T = TypeVar("T")

def run_coroutine_sync(coroutine: Coroutine[Any, Any, T], timeout: float = 30) -> T:
    def run_in_new_loop():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coroutine)
        finally:
            new_loop.close()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coroutine)

    if threading.current_thread() is threading.main_thread():
        if not loop.is_running():
            return loop.run_until_complete(coroutine)
        else:
            with ThreadPoolExecutor() as pool:
                future = pool.submit(run_in_new_loop)
                return future.result(timeout=timeout)
    else:
        return asyncio.run_coroutine_threadsafe(coroutine, loop).result()