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
    packages=[
        "coldtype"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
