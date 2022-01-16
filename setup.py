import setuptools

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.com](https://coldtype.goodhertz.com)
"""

setuptools.setup(
    name="coldtype",
    version="0.9.0",
    author="Rob Stenson / Goodhertz",
    author_email="rob@goodhertz.com",
    description="Functions for manual vectorized typesetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goodhertz/coldtype",
    #package_dir={"": "coldtype"},
    packages=[
        "coldtype",
        "coldtype.fx",
        "coldtype.img",
        "coldtype.time",
        "coldtype.midi",
        "coldtype.pens",
        "coldtype.text",
        "coldtype.grid",
        "coldtype.color",
        "coldtype.runon",
        "coldtype.capture",
        "coldtype.blender",
        "coldtype.geometry",
        "coldtype.time.nle",
        "coldtype.renderer",
        "coldtype.renderable",
        "coldtype.fontgoggles",
        "coldtype.interpolation",
        "coldtype.runon.mixins",
        "coldtype.renderer.winman",
        "coldtype.fontgoggles.font",
        "coldtype.fontgoggles.misc",
        "coldtype.fontgoggles.compile",
    ],
    include_package_data=True,
    package_data={
        "": [
            "demo/RecMono-CasualItalic.ttf",
            "demo/ColdtypeObviously-VF.ttf",
            "demo/MutatorSans.ttf",
            "demo/demo.py",
            "demo/glyphs.py",
            "demo/midi.py",
            "demo/blank.py",
            "demo/boiler.py",
            "demo/vf.py",
            "renderer/picklejar.py",
            "renderer/.coldtype.py"
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
            "skia-python>=86.0",
            "skia-pathops", # can this be taken from skia-python?
            "ufo2ft",
            "numpy",
        ],
        "experimental": [
            "pynput",
            "rtmidi",
            "noise",
        ],
        "c": [
            #"srt",
            "noise",
        ],
        "unicode": [
            "unicodedata2"
        ],
        "blender": [
            "skia-pathops"
        ],
        "notebook": [
            "skia-pathops",
            "skia-python",
        ],
        "audio": [
            "pyaudio",
            "soundfile",
        ]
    },
    install_requires=[
        "fonttools[ufo]",
        "fontPens",
        "easing-functions",
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
