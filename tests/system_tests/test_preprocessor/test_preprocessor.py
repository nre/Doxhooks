from doxhooks.errors import DoxhooksDataError
from pytest import raises

from doxhooks_pytest import OutputFilesTest


class TestPreprocessor(OutputFilesTest):
    user_module_name = "feature"
    output_directory = "output"

    def test_the_output_files_match_the_established_output_files(self, capsys):
        self.user_module.update_preprocessor_features()

        self.user_module.update_warning_directive()
        __, stderr = capsys.readouterr()
        assert stderr.endswith("Test the warning directive.\n")

        with raises(DoxhooksDataError):
            self.user_module.update_error_directive()

        self.assert_the_output_files_match_the_established_output_files()
