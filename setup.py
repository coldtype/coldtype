import setuptools

long_description = """
# Coldtype

### Programmatic display typography

More info available at: [coldtype.goodhertz.co](https://coldtype.goodhertz.co)
"""

setuptools.setup(
    name="coldtype",
    version="0.0.5",
    author="Rob Stenson / Goodhertz",
    author_email="rob@goodhertz.com",
    description="Functions for manual vectorized typesetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goodhertz/coldtype",
    #package_dir={"": "coldtype"},
    packages=[
        "coldtype",
        "coldtype.animation",
        "coldtype.color",
        "coldtype.pens",
        "coldtype.renderer",
        "coldtype.text",
        "coldtype.fontgoggles",
        "coldtype.fontgoggles.compile",
        "coldtype.fontgoggles.font",
        "coldtype.fontgoggles.misc",
    ],
    entry_points={
        'console_scripts': [
            'coldtype = coldtype.renderer:main'
        ],
    },
    extras_require={
        #"drawbot": [
        #    "drawbot @ http://github.com/typemytype/drawbot/archive/master.zip"
        #],
        "renderer": [
            "noise",
            "websocket-client",
            "websockets",
            "watchdog",
        ]
    },
    install_requires=[
        "fontPens",
        "defcon",
        "mido",
        "skia-pathops",
        "easing-functions",
        "fonttools[woff,unicode,type1,lxml,ufo]",
        "freetype-py",
        "uharfbuzz",
        "python-bidi",
        "ufo2ft",
        "unicodedata2",
        "numpy",
        #"fontgoggles @ http://github.com/goodhertz/fontgoggles/archive/master.zip"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
