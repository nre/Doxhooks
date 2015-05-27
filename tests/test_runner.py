import os
import re
import sys

import pytest
from coverage import coverage


dist_name = "doxhooks"
packages = ["doxhooks"]

tests_path = os.path.dirname(os.path.abspath(__file__))
unit_tests_path = os.path.join(tests_path, "unit_tests")
component_tests_path = os.path.join(tests_path, "component_tests")
system_tests_path = os.path.join(tests_path, "system_tests")
example_tests_path = os.path.join(tests_path, "example_tests")
dist_path = os.path.normpath(os.path.join(tests_path, os.pardir))
pkg_paths = [os.path.join(dist_path, pkg) for pkg in packages]


def fail(*args):
    error_message = "[test_runner] " + " ".join(map(str, args))
    sys.exit(error_message)


def get_import_name(*args):
    import_path = os.path.normpath(os.path.join(dist_name, *args))
    return import_path.replace(os.sep, ".")


def pytest_main(args):
    if isinstance(args, str):
        args = args,
    # pytest does not recognise backslash as a path separator:
    if os.sep != "/":
        args = [string.replace(os.sep, "/") for string in args]
    exit_code = pytest.main(args)
    if exit_code:
        fail("pytest returned", exit_code)


def coverage_test(source, pytest_args):
    cov = coverage(source=[source])
    cov.start()
    try:
        pytest_main(pytest_args)
    finally:
        cov.stop()
    print()  # Print blank line.
    cov.report(show_missing=False)
    cov.html_report()


def unit_test(path):
    dir_path, file = os.path.split(path)
    match = re.match("test_(?P<module>\w*)\.py$", file)
    module = match.group("module")
    pkgs = os.path.relpath(dir_path, unit_tests_path)
    import_name = get_import_name(pkgs, module)
    coverage_test(import_name, path)


def test_all():
    test_order = [
        unit_tests_path,
        component_tests_path,
        system_tests_path,
        example_tests_path,
    ]
    coverage_test(dist_name, test_order)


def find_unit_test_for_source_file(relpath):
    pkgs_module, __ = os.path.splitext(relpath)
    import_name = get_import_name(pkgs_module)
    dirs, file = os.path.split(relpath)
    test_path = os.path.join(unit_tests_path, dirs, "test_" + file)
    if not os.path.exists(test_path):
        fail("Test path not found:", test_path)
    coverage_test(import_name, test_path)


def main(arg_path):
    path = os.path.abspath(arg_path)
    __, filename = os.path.split(path)

    if path.startswith(tests_path):
        if not filename.startswith("test_"):
            fail("Not a test file:", path)
        elif path.startswith(unit_tests_path):
            unit_test(path)
        elif (path.startswith(component_tests_path) or
                path.startswith(system_tests_path) or
                path.startswith(example_tests_path)):
            pytest_main(path)
        return
    for pkg_path in pkg_paths:
        if path.startswith(pkg_path):
            relpath = os.path.relpath(path, pkg_path)
            find_unit_test_for_source_file(relpath)
            return
    fail("Path not handled:", path)


if __name__ == "__main__":
    try:
        arg_path = sys.argv[1]
    except IndexError:
        arg_path = None

    if arg_path is not None:
        main(arg_path)
    else:
        test_all()
