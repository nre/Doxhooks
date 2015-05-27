from doxhooks_pytest import OutputFilesTest


class TestPreprocessor(OutputFilesTest):
    user_module_name = "feature"
    output_directory = "output"

    def test_the_output_files_match_the_established_output_files(self, capsys):
        self.user_module.update_html_preprocessor()
        __, stderr = capsys.readouterr()
        assert stderr.endswith("Unknown HTML character reference: unknown\n")

        self.user_module.update_silent_html_preprocessor()
        __, stderr = capsys.readouterr()
        assert not stderr

        self.assert_the_output_files_match_the_established_output_files()
