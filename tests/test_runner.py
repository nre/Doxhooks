#!/usr/bin/env python3
import os
import re
import sys
from argparse import ArgumentParser
from functools import partial

import pytest
from coverage import Coverage


DIST_NAME = "doxhooks"
PACKAGES = {"doxhooks"}

TESTS_ROOT = os.path.dirname(os.path.abspath(__file__))
DIST_ROOT = os.path.normpath(os.path.join(TESTS_ROOT, os.pardir))
PACKAGE_ROOTS = {os.path.join(DIST_ROOT, pkg) for pkg in PACKAGES}

UNIT_TESTS_ROOT = os.path.join(TESTS_ROOT, "unit_tests")
COMPONENT_TESTS_ROOT = os.path.join(TESTS_ROOT, "component_tests")
SYSTEM_TESTS_ROOT = os.path.join(TESTS_ROOT, "system_tests")
EXAMPLE_TESTS_ROOT = os.path.join(TESTS_ROOT, "example_tests")

ALL_TEST_ROOTS = [
    UNIT_TESTS_ROOT,
    COMPONENT_TESTS_ROOT,
    SYSTEM_TESTS_ROOT,
    EXAMPLE_TESTS_ROOT,
]


def error_message(*args):
    sys.exit(" ".join(map(str, args)))


def first_truthy(iterable):
    return next(filter(None, iterable), None)


def list_of_str(args):
    return [args] if isinstance(args, str) else args


def dot_path(path):
    stem, __ = os.path.splitext(os.path.normpath(path))
    return stem.replace(os.sep, ".")


def slash_path(path):
    return path.replace(os.sep, "/")


def is_subpath(path, root):
    rel_path = os.path.normpath(os.path.relpath(path, root))
    return not rel_path.startswith(os.pardir)


def is_test_file(path):
    __, filename = os.path.split(path)
    return filename.startswith("test_")


def pytest_main(args):
    # NB: pytest does not recognise backslash as a path separator.
    paths = [slash_path(path) for path in list_of_str(args)]
    missing_files = [path for path in paths if not os.path.exists(path)]
    if missing_files:
        plural = "s" if len(missing_files) > 1 else ""
        error_message("Test{} not found:".format(plural), *missing_files)
    return pytest.main(paths)


def all_test_roots_if_none(arg):
    return ALL_TEST_ROOTS if arg is None else None


def is_unit_test(path):
    return is_subpath(path, UNIT_TESTS_ROOT) and is_test_file(path)


def is_integration_test(path):
    roots = COMPONENT_TESTS_ROOT, SYSTEM_TESTS_ROOT, EXAMPLE_TESTS_ROOT
    return (any(is_subpath(path, root) for root in roots) and
            is_test_file(path))


def path_if_unit_test_path(path):
    return path if is_unit_test(path) else None


def path_if_integration_test_path(path):
    return path if is_integration_test(path) else None


def unit_test_path(source_path, pkg_root):
    rel_source_path = os.path.relpath(source_path, pkg_root)
    rel_dir_path, file = os.path.split(rel_source_path)
    return os.path.join(UNIT_TESTS_ROOT, rel_dir_path, "test_" + file)


def unit_test_path_if_source_file(path):
    return first_truthy(
        (unit_test_path(path, pkg_root) for pkg_root in PACKAGE_ROOTS
            if is_subpath(path, pkg_root))
    )


def compute_pytest_args(path):
    return first_truthy(
        (f(path) for f in [
            all_test_roots_if_none,
            path_if_unit_test_path,
            path_if_integration_test_path,
            unit_test_path_if_source_file,
            partial(error_message, "Path not handled:"),
        ])
    )


def unit_of_unit_test(test_path):
    dirs, file = os.path.split(os.path.relpath(test_path, UNIT_TESTS_ROOT))
    module = re.match("test_(?P<module>\w+)\.py$", file).group("module")
    return dot_path(os.path.join(DIST_NAME, dirs, module))


def coverage_kwargs(pytest_args):
    if pytest_args is ALL_TEST_ROOTS:
        source = DIST_NAME
        report = True
    elif is_unit_test(pytest_args):
        source = unit_of_unit_test(pytest_args)
        report = True
    else:
        source = DIST_NAME
        report = False
    return dict(source=source, report=report)


def with_coverage(f, source, *, report=True, data=False):
    cov = Coverage(source=[source])
    cov.start()
    try:
        exit_code = f()
    finally:
        cov.stop()
    if not exit_code:
        if report:
            print()  # Print blank line.
            cov.report(show_missing=False)
            cov.html_report()
        if data:
            cov.save()
    return exit_code


def parse_args():
    parser = ArgumentParser(description="Run the Doxhooks tests.")
    parser.add_argument(
        "path", help="path to source file or test file", nargs="?")
    parser.add_argument(
        "--data", help="save coverage data", action="store_true")
    args = parser.parse_args()

    return dict(path=args.path, data=args.data)


def main(path=None, *, data=False):
    if path is not None:
        path = os.path.abspath(path)

    pytest_args = compute_pytest_args(path)

    # - coverage imports from cwd in preference to sys.path. This causes
    #   problems if the cwd is DIST_ROOT because coverage imports the
    #   package directory instead of the package module.
    # - coverage config and output files go in TESTS_ROOT.
    # - Paths in pytest stdout are easier to read relative to TESTS_ROOT.
    cwd = os.getcwd()
    os.chdir(TESTS_ROOT)

    try:
        return with_coverage(
            partial(pytest_main, pytest_args),
            data=data,
            **coverage_kwargs(pytest_args)
        )
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    sys.exit(main(**parse_args()))
