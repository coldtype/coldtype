import setuptools

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.com](https://coldtype.goodhertz.com)
"""

setuptools.setup(
    name="coldtype",
    version="0.5.18",
    author="Rob Stenson / Goodhertz",
    author_email="rob@goodhertz.com",
    description="Functions for manual vectorized typesetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goodhertz/coldtype",
    #package_dir={"": "coldtype"},
    packages=[
        "coldtype",
        "coldtype.sh",
        "coldtype.fx",
        "coldtype.img",
        "coldtype.time",
        "coldtype.midi",
        "coldtype.pens",
        "coldtype.text",
        "coldtype.grid",
        "coldtype.color",
        "coldtype.capture",
        "coldtype.blender",
        "coldtype.geometry",
        "coldtype.time.nle",
        "coldtype.renderer",
        "coldtype.webserver",
        "coldtype.renderable",
        "coldtype.fontgoggles",
        "coldtype.interpolation",
        "coldtype.renderer.winman",
        "coldtype.fontgoggles.font",
        "coldtype.fontgoggles.misc",
        "coldtype.fontgoggles.compile",
    ],
    include_package_data=True,
    package_data={
        "": [
            "webserver/webviewer.html",
            "demo/RecMono-CasualItalic.ttf",
            "demo/ColdtypeObviously-VF.ttf",
            "demo/MutatorSans.ttf",
            "demo/demo.py",
            "demo/blank.py",
            "demo/boiler.py",
            "renderer/picklejar.py",
        ],
    },
    entry_points={
        'console_scripts': [
            'coldtype = coldtype.renderer:main'
        ],
    },
    extras_require={
        "skia": [
            "skia-python>=86.0",
        ],
        "viewer": [
            "glfw",
            "PyOpenGL",
            "PyOpenGL-accelerate",
            "skia-python>=86.0",
            "skia-pathops", # can this be taken from skia-python?
            "SimpleWebSocketServer",
            "watchdog<2.0.0", # https://github.com/gorakhargosh/watchdog/issues/702
            "noise",
            "ufo2ft",
            "numpy",
        ],
        "webviewer": [
            "SimpleWebSocketServer",
            "watchdog<2.0.0", # https://github.com/gorakhargosh/watchdog/issues/702
        ],
        "experimental": [
            "pynput",
            "rtmidi",
            "noise",
        ],
        "c": [
            "srt",
            "noise",
        ],
        "unicode": [
            "unicodedata2"
        ],
        "blender": [
            "skia-pathops"
        ]
    },
    install_requires=[
        "lxml",
        "fonttools[ufo]",
        "fontPens",
        "fontParts",
        "more-itertools",
        "easing-functions",
        "timecode",
        "mido",
        "defcon",
        "freetype-py",
        "uharfbuzz>=0.14.0",
        "python-bidi"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
