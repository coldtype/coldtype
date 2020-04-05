import setuptools

long_description = """
### Coldtype
"""

setuptools.setup(
    name="coldtype",
    version="0.0.1",
    author="Rob Stenson / Goodhertz",
    author_email="rob@goodhertz.com",
    description="Functions for manual vectorized typesetting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goodhertz/coldtype",
    #package_dir={"": "coldtype"},
    packages=[
        "coldtype",
        "coldtype.color",
        "coldtype.pens",
        "coldtype.renderer",
        "coldtype.text",
    ],
    entry_points={
        'console_scripts': [
            'coldtype = coldtype.renderer:main'
        ],
    },
    install_requires=[
        "fontPens",
        "defcon",
        "noise",
        "skia-pathops",
        "websocket-client",
        "websockets",
        "watchdog",
        "fonttools[woff,unicode,type1,lxml,ufo]",
        "freetype-py",
        "uharfbuzz",
        "python-bidi",
        "ufo2ft",
        #"unicodedata2",
        "numpy",
        "fontgoggles @ http://github.com/goodhertz/fontgoggles/archive/master.zip"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
