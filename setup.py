import setuptools

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.com](https://coldtype.goodhertz.com)
"""

setuptools.setup(
    name="coldtype",
    version="0.3.4",
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
    include_package_data=True,
    package_data={
        "": ["webserver/webviewer.html"],
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
            "rtmidi",
        ],
        "experimental": [
            "pynput",
            "pyaudio",
        ]
    },
    install_requires=[
        "drafting[text]>=0.1.8",
        "srt",
        "mido",
        "numpy",
        "noise",
        "defcon",
        "docutils",
        "timecode",
        "more-itertools",
        "easing-functions",
        "SimpleWebSocketServer",
        "watchdog<2.0.0", # https://github.com/gorakhargosh/watchdog/issues/702
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
