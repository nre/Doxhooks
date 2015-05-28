#!/usr/bin/env python3
import os
import subprocess


source_dir = os.path.dirname(__file__)
build_dir = os.path.join(source_dir, "__htmldocs__")

cmd = "sphinx-build -b {{}} {} {}".format(source_dir, build_dir)


if __name__ == "__main__":
    subprocess.check_call(cmd.format("doctest"))
    subprocess.check_call(cmd.format("html -a"))
