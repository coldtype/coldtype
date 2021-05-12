import setuptools

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.com](https://coldtype.goodhertz.com)
"""

setuptools.setup(
    name="coldtype",
    version="0.3.2",
    author="Rob Stenson / Goodhertz",
    author_email="rob@goodhertz.com",
    description="Functions for manual vectorized typesetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goodhertz/coldtype",
    #package_dir={"": "coldtype"},
    packages=[
        "coldtype",
        "coldtype.time",
        "coldtype.midi",
        "coldtype.pens",
        "coldtype.text",
        "coldtype.capture",
        "coldtype.time.nle",
        "coldtype.renderer",
        "coldtype.renderable",
        "coldtype.webserver",
    ],
    entry_points={
        'console_scripts': [
            'coldtype = coldtype.renderer:main'
        ],
    },
    install_requires=[
        "drafting>=0.1.3",
        "defcon",
        "mido",
        "skia-python>=86.0",
        "easing-functions",
        "numpy",
        "watchdog<2.0.0", # https://github.com/gorakhargosh/watchdog/issues/702
        "noise",
        "PyOpenGL",
        "PyOpenGL-accelerate",
        "glfw",
        "SimpleWebSocketServer",
        "more-itertools",
        "docutils",
        "exdown",
        "srt",
        "timecode",
        #"rtmidi",
        #"pynput",
        #"pyaudio",
        #"websocket-client",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
