import math
import sys
import os
import re
import copy

name = "coldtype"
dirname = os.path.dirname(__file__)

#from pathlib import Path
#if __name__ == "__main__":
#    sys.path.insert(0, str(Path(__file__).parent.parent.resolve())) #os.path.realpath(dirname + "/.."))

from coldtype.text import *
from coldtype.pens.datpen import DATPen, DATPenSet
from coldtype.geometry import Rect