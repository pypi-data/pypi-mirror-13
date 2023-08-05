"""
This module provides the setup guidelines for the normalazy library.
"""

from distutils.core import setup
from normalazy import __version__

## Setup now:
setup(
    name="normalazy",
    version=__version__,
    description="A mapper to normalize records for lazy people",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries",
    ],
    keywords=["normalizer", "DSL"],
    author="Vehbi Sinan Tunalioglu",
    author_email="vst@vsthost.com",
    url="https://github.com/vst/normalazy",
    py_modules=["normalazy"],
)
