from setuptools import setup

from doxhooks import __version__


with open("README.rst") as readme:
    lines = list(readme)[3:]  # Title takes up first three lines.
    long_description = "".join(lines)

setup(
    name="Doxhooks",
    version=__version__,

    description=(
        "Abstract away the content and maintenance of files in your project."
    ),
    long_description=long_description,

    url="https://github.com/nre/doxhooks",

    author="Nick Evans",
    author_email="nre@users.noreply.github.com",

    license="MIT",

    keywords=(
        "abstract, build, code, document, file, hook, "
        "preprocessor, project, resource, source, text"
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Pre-processors",
    ],

    packages=["doxhooks"],
)