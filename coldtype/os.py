import platform, os
from enum import Enum

class System(Enum):
    Darwin = "Darwin"
    Windows = "Windows"
    Linux = "Linux"

def operating_system():
    sys = platform.system()
    if sys == "Darwin":
        return System.Darwin
    elif sys == "Windows":
        return System.Windows
    elif sys == "Linux":
        return System.Linux


def on_windows():
    return operating_system() == System.Windows

def on_mac():
    return operating_system() == System.Darwin

def on_linux():
    return operating_system() == System.Linux


def play_sound(name="Pop"):
    """
    easy sound-playing utility
    should be implemented on other
    platforms as well
    """
    if on_mac():
        os.system(f"afplay /System/Library/Sounds/{name}.aiff")