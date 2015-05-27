import doxhooks.console as console
from pytest import fixture, raises


class BaseTestConsole:
    @fixture(autouse=True)
    def _setup_capsys(self, capsys):
        self.capsys = capsys


class TestStdOut(BaseTestConsole):
    def _assert(self, string):
        stdout, stderr = self.capsys.readouterr()
        assert stdout == string
        assert not stderr

    def test_important_status_information_is_prominent_in_stdout(self):
        # When reporting important status information
        console.info("test info", 1)
        # then the information is prominent in stdout.
        self._assert("test info 1\n")

    def test_general_status_information_is_less_prominent_in_stdout(self):
        # When reporting general status information
        console.log("test log", 1)
        # then the information is less prominent in stdout.
        self._assert("    test log 1\n")

    def test_preformatted_information_is_reproduced_verbatim_in_stdout(self):
        # When reporting preformatted information
        console.pre("  test\n    pre")
        # then the information is reproduced verbatim in stdout.
        self._assert("  test\n    pre\n")

    def test_a_section_break_is_obvious_in_stdout(self):
        # When reporting a new section of information
        console.section()
        # then the section break is obvious in stdout.
        section_break = (
            "\n\n"
            "####################"
            "###########################################################"
            "\n\n")
        self._assert(section_break)

    def test_a_section_heading_is_obvious_in_stdout(self):
        # When reporting a new section of information
        # and the section has a name
        console.section("test heading")
        # then the section break and heading are obvious in stdout.
        section_heading = (
            "\n\n"
            "### test heading ###"
            "###########################################################"
            "\n\n")
        self._assert(section_heading)

    def test_a_blank_line_written_to_stdout_is_explicit_in_the_source_code(
            self):
        # When writing a blank line to stdout
        console.blank_line()
        # then the blank line is explicit in the source code.
        self._assert("\n")


class TestStdErr(BaseTestConsole):
    def _assert(self, string):
        stdout, stderr = self.capsys.readouterr()
        assert stderr == string
        assert not stdout

    def test_error_information_is_prominent_in_stderr(self):
        # When reporting an error
        console.error("test error", 1)
        # then the information is prominent in stderr.
        self._assert(" ** Error! test error 1\n")

    def test_type_and_message_of_an_error_object_are_prominent_in_stderr(self):
        # When reporting an error object
        console.error(BaseException("test error"), 1)
        # then the error type and message are prominent in stderr.
        self._assert(" ** BaseException! test error 1\n")

    def test_error_trace_information_is_prominent_in_stderr(self):
        # When reporting an error trace
        console.error_trace("test location", "test source")
        # then the location and source are prominent in stderr.
        self._assert(" ** Error trace! test location: test source\n")

    def test_a_warning_message_is_less_prominent_in_stderr(self):
        # When reporting a warning
        console.warning("test warning", 1)
        # then the information is less prominent in stderr.
        self._assert("  * Warning! test warning 1\n")

    def test_a_stdin_prompt_is_prominent_in_stderr(self):
        # When prompting the user for input
        with raises(OSError):
            console.input("test prompt")
        # then the prompt is prominent in stderr.
        self._assert(" >> test prompt")
