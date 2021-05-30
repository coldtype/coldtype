import os
import tempfile

from .dsCompiler import compileDSToPath
from .ufoCompiler import compileUFOToPath as ufo_compileUFOToPath
from .ttxCompiler import compileTTXToPath

def compileUFOToPath(ufoPath, ttPath, outputWriter):
    return ufo_compileUFOToPath(os.fspath(ufoPath), os.fspath(ttPath))

def compileUFOToBytes(ufoPath, outputWriter):
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf") as tmp:
        compileUFOToPath(ufoPath, tmp.name, outputWriter)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    return fontData


def compileDSToBytes(dsPath, ttFolder, outputWriter):
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf") as tmp:
        compileDSToPath(dsPath, ttFolder, tmp.name)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    return fontData


def compileTTXToBytes(ttxPath, outputWriter):
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf") as tmp:
        compileTTXToPath(ttxPath, tmp.name)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    return fontData