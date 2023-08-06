

from setuptools import setup
setup(
    name = "ctext",
    packages = ["ctext"],
    version = "0.11",
    description = "Chinese Text Project API wrapper",
    author = "Donald Sturgeon",
    author_email = "chinesetextproject@gmail.com",
    url = "http://ctext.org/tools/api",
    keywords = ["Chinese", "text", "API", "ctext"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        ],
    long_description = """\
Python wrapper around the CTP API
---------------------------------

This software is incomplete and experimental.
See http://ctext.org/tools/api for API details.

Requires Python 3 or later.
"""
)
