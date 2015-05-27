import os

from doxhooks_pytest import ExampleTestDriver, examples_path


this_module = vars()

# Define a test class for each example dir.
for subdir in os.listdir(examples_path):
    subdir_path = os.path.join(examples_path, subdir)

    if not os.path.isdir(subdir_path):
        continue

    for example_dir in os.listdir(subdir_path):
        example_dir_path = os.path.join(subdir_path, example_dir)

        if not os.path.isdir(example_dir_path):
            continue

        test_class_name = "Test" + example_dir.title().replace("_", "")

        # Define a test class.
        this_module[test_class_name] = type(
            test_class_name,
            (ExampleTestDriver,),
            {"dir_path": example_dir_path},
        )
