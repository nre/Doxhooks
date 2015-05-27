import os
import re

from doxhooks_pytest import SystemTestDriver


system_tests_path = os.path.dirname(__file__)
this_module = vars()

match_test_script = re.compile(r"test_\w*\.py$").match

# Define a test class for each test dir that does not have a test script.
for test_dir in os.listdir(system_tests_path):
    test_dir_path = os.path.join(system_tests_path, test_dir)

    if not (test_dir.startswith("test_") and os.path.isdir(test_dir_path)):
        continue

    for entry in os.listdir(test_dir_path):
        if match_test_script(entry):
            test_dir_has_a_test_script = True
            break
    else:
        test_dir_has_a_test_script = False

    if test_dir_has_a_test_script:
        continue

    test_class_name = test_dir.title().replace("_", "")

    # Define a test class for this test dir.
    this_module[test_class_name] = type(
        test_class_name,
        (SystemTestDriver,),
        {"dir_path": test_dir_path},
    )
