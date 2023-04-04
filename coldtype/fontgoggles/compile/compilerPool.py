import os
import tempfile

from .dsCompiler import compileDSToPath
from .ufoCompiler import compileUFOToPath as ufo_compileUFOToPath
from .ttxCompiler import compileTTXToPath

def compileUFOToPath(ufoPath, ttPath, outputWriter):
    return ufo_compileUFOToPath(os.fspath(ufoPath), os.fspath(ttPath))

def compileUFOToBytes(ufoPath, outputWriter):
    to_delete = None
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf", mode="wb", delete=False) as tmp:
        to_delete = tmp
        compileUFOToPath(ufoPath, tmp.name, outputWriter)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    if to_delete:
        to_delete.close()
        os.unlink(to_delete.name)
    return fontData


def compileDSToBytes(dsPath, ttFolder, outputWriter):
    to_delete = None
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf", mode="wb", delete=False) as tmp:
        to_delete = tmp
        compileDSToPath(dsPath, ttFolder, tmp.name)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    if to_delete:
        to_delete.close()
        os.unlink(to_delete.name)
    return fontData


def compileTTXToBytes(ttxPath, outputWriter):
    with tempfile.NamedTemporaryFile(prefix="fontgoggles_temp", suffix=".ttf") as tmp:
        compileTTXToPath(ttxPath, tmp.name)
        with open(tmp.name, "rb") as f:
            fontData = f.read()
            if not fontData:
                fontData = None
    return fontData