import setuptools, sys

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.com](https://coldtype.goodhertz.com)
"""

basic_deps = [
    "fontPens==0.2.4",
    "easing-functions==1.0.4",
    "mido==1.3.2",
    "defcon==0.10.3",
    "requests==2.32.3",
    "b3denv>=0.0.12",
    "ufo2ft==3.2.8", # pin for an issue in fg
    "coldtype-fontgoggles>=1.8.4",
]

#if sys.platform.startswith("darwin"):
#    basic_deps.extend(["pyobjc-framework-Cocoa", "pyobjc-framework-CoreText"])

setuptools.setup(
    name="coldtype",
    version="0.11.1",
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
        "coldtype.web",
        "coldtype.midi",
        "coldtype.pens",
        "coldtype.text",
        "coldtype.grid",
        "coldtype.color",
        "coldtype.runon",
        "coldtype.timing",
        "coldtype.physics",
        "coldtype.capture",
        "coldtype.blender",
        "coldtype.geometry",
        "coldtype.timing.nle",
        "coldtype.notebook",
        "coldtype.renderer",
        "coldtype.text.colr",
        "coldtype.renderable",
        "coldtype.interpolation",
        "coldtype.runon.mixins",
        "coldtype.renderer.winman",
    ],
    include_package_data=True,
    package_data={
        "": [
            "assets/glyphNamesToUnicode.txt",
            "demo/transparency_blocks.png",
            "demo/RecMono-CasualItalic.ttf",
            "demo/ColdtypeObviously-VF.ttf",
            "demo/JetBrainsMono.ttf",
            "demo/MutatorSans.ttf",
            "demo/demo.py",
            "demo/glyphs.py",
            "demo/glyphloop.py",
            "demo/midi.py",
            "demo/blank.py",
            "demo/boiler.py",
            "demo/boiler_renderable.py",
            "demo/vf.py",
            "demo/gifski.py",
            "demo/glfw34.py",
            "renderer/.coldtype.py",
            "web/templates/page.j2",
            "web/templates/notebook.j2",
        ],
    },
    entry_points={
        'console_scripts': [
            'coldtype = coldtype.renderer:main',
            'ct = coldtype.renderer:main',
            'ctb = coldtype.renderer:main_b3d',
        ],
    },
    extras_require={
        "drawbot": [
            "numpy",
        ],
        "viewer": [
            "glfw",
            "PyOpenGL",
            "skia-pathops", # can this be taken from skia-python?
            "ufo2ft",
            #"ufoLib2",
            "numpy",
            "potracer",
        ],
        "viewer:python_version < '3.12'": [
            "skia-python==87.5",
        ],
        "viewer:python_version >= '3.12'": [
            "skia-python>87.5",
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
            "skia-pathops",
            "ufo2ft",
            "ufoLib2", # temporary for a bug in ufo2ft
        ],
        "notebook": [
            "skia-pathops",
            "skia-python",
            "potracer",
            "tdqm",
        ],
        "audio": [
            "pyaudio",
            "soundfile",
        ],
        "website": [
            "jinja2",
            "python-frontmatter",
            "livereload",
            "Markdown",
            "markdown-captions",
            "beautifulsoup4",
            "brotli",
            "lxml",
            "pygments",
            "sourcetypes",
            "favicons",
        ]
    },
    install_requires=basic_deps,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
