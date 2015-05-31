#!/usr/bin/env python3
from setuptools import setup

from doxhooks import __version__


with open("README.rst") as readme:
    lines = list(readme)

for line_no, line in enumerate(lines):
    if line.startswith("Doxhooks helps you"):
        long_description = "".join(lines[line_no:])
        break
else:
    raise RuntimeError("Cannot find long description in README.")


setup(
    name="Doxhooks",
    version=__version__,

    description=(
        "Abstract away the content and maintenance of files in your project."
    ),
    long_description=long_description,

    url="https://github.com/nre/doxhooks",

    author="Nick Evans",
    author_email="nick.evans3976@gmail.com",

    license="MIT",

    keywords=(
        "abstract build code document file hook "
        "preprocessor project resource source text"
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Pre-processors",
    ],

    packages=["doxhooks"],
)
