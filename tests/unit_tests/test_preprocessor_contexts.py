from types import SimpleNamespace

from doxhooks.errors import (
    DoxhooksDataError, DoxhooksLookupError, DoxhooksTypeError)
from doxhooks.preprocessor_contexts import (
    BasePreprocessorContext, PreprocessorContext, lowercase_booleans,
    startcase_booleans)
from pytest import mark

from doxhooks_pytest import withraises


class BaseTestBasePreprocessorContext:
    name = "test_name"
    Context = BasePreprocessorContext

    def given_a_preprocessor_context(self, **variables):
        self.context = self.Context(**variables)

    def given_a_preprocessor_context_with_a_variable(self, value):
        variables = {}
        variables[self.name] = value
        self.given_a_preprocessor_context(**variables)

    @withraises
    def when_getting_the_value_of_a_token(self, token):
        self.got_value = self.context.get(token)

    @withraises
    def when_getting_the_value_of_the_variable(self):
        self.when_getting_the_value_of_a_token(self.name)

    def then_a_string_representation_of_that_value_is_returned(self, str_repr):
        assert self.got_value == str_repr

    @withraises
    def when_interpreting_a_keyword_and_its_tokens(
            self, keyword_token, *tokens):
        self.context.interpret(keyword_token, *tokens, preprocessor=None)


class TestOutputTypes(BaseTestBasePreprocessorContext):
    @mark.parametrize(
        "value, str_repr", [
            (1, "1"), (1.23, "1.23"), ("string", "string")
        ])
    def test_a_context_returns_a_string_representation_of_an_output_type(
            self, value, str_repr):
        self.given_a_preprocessor_context_with_a_variable(value)

        self.when_getting_the_value_of_the_variable()

        self.then_a_string_representation_of_that_value_is_returned(str_repr)

    @mark.parametrize(
        "non_output_value", [
            None, True, False, b"bytes", [], (), {}, set()
        ])
    def test_getting_the_value_of_a_non_output_type_is_an_error(
            self, non_output_value):
        self.given_a_preprocessor_context_with_a_variable(non_output_value)

        self.when_getting_the_value_of_the_variable(raises=DoxhooksTypeError)

        assert self.error.value == non_output_value

    def _make_context_subclass(self):
        return type("ContextSubclass", (BasePreprocessorContext,), {})

    @mark.parametrize(
        "decorator, bool_value, str_repr", [
            (lowercase_booleans, True, "true"),
            (lowercase_booleans, False, "false"),
            (startcase_booleans, True, "True"),
            (startcase_booleans, False, "False"),
        ])
    def test_the_boolean_type_is_an_output_type_in_a_modified_context(
            self, decorator, bool_value, str_repr):
        self.Context = decorator(self._make_context_subclass())
        self.given_a_preprocessor_context_with_a_variable(bool_value)

        self.when_getting_the_value_of_the_variable()

        self.then_a_string_representation_of_that_value_is_returned(str_repr)


class TestMemberOperator(BaseTestBasePreprocessorContext):
    value = "test_value"

    class Context(BasePreprocessorContext):
        pass

    Context.one = SimpleNamespace()
    Context.one.name = value
    Context.one.two = SimpleNamespace()
    Context.one.two.name = value

    @mark.parametrize("token", ["one.name", "one.two.name"])
    def test_member_operators_in_an_identifier_token_are_evaluated(
            self, token):
        self.given_a_preprocessor_context()

        self.when_getting_the_value_of_a_token(token)

        self.then_a_string_representation_of_that_value_is_returned(self.value)

    @mark.parametrize(
        "token, description", [
            ("x", "preprocessor context"),
            ("one.x", "`one`"),
            ("one.two.x", "`one.two`"),
        ])
    def test_getting_the_value_of_an_undefined_identifier_is_an_error(
            self, token, description):
        self.given_a_preprocessor_context()

        self.when_getting_the_value_of_a_token(
            token, raises=DoxhooksLookupError)

        assert self.error.description == description


class TestInterpret(BaseTestBasePreprocessorContext):
    class Context(BasePreprocessorContext):
        not_a_method = True

        def keyword_takes_one_arg(self, arg, *, preprocessor=None):
            pass

    def test_interpreting_a_token_that_is_not_callable_is_an_error(self):
        self.given_a_preprocessor_context()

        self.when_interpreting_a_keyword_and_its_tokens(
            "not_a_method", raises=DoxhooksTypeError)

        assert self.error.value == self.context.not_a_method

    @mark.parametrize(
        "wrong_args", [(), (0, 1)])
    def test_interpreting_a_keyword_with_bad_syntax_is_an_error(
            self, wrong_args):
        self.given_a_preprocessor_context()

        self.when_interpreting_a_keyword_and_its_tokens(
            "keyword_takes_one_arg", *wrong_args, raises=DoxhooksDataError)

        assert self.error


class TestSet(BaseTestBasePreprocessorContext):
    Context = PreprocessorContext

    @mark.parametrize(
        "str_value, value", [
            ("1", 1),
            ("1 + 1", 2),
            ("1.23", 1.23),
            ("True", True),
            ("string", "string"),
        ])
    def test_a_value_token_is_evaluated_before_setting_a_variable(
            self, str_value, value):
        self.given_a_preprocessor_context()

        self.when_interpreting_a_keyword_and_its_tokens(
            "set", self.name, str_value)

        # then the variable is set to the value of the evaluated token.
        context_value = getattr(self.context, self.name)
        assert context_value == value


class TestConditionToken(BaseTestBasePreprocessorContext):
    class Context(PreprocessorContext):
        not_bool = None

    def test_interpreting_a_non_boolean_condition_is_an_error(self):
        self.given_a_preprocessor_context()

        self.when_interpreting_a_keyword_and_its_tokens(
            "if", "not_bool", "dummy_keyword", raises=DoxhooksTypeError)

        assert self.error.value == self.context.not_bool


class TestFileToken(BaseTestBasePreprocessorContext):
    class Context(PreprocessorContext):
        not_str_or_none = True

    def test_a_bad_type_of_file_token_is_an_error(self):
        self.given_a_preprocessor_context()

        self.when_interpreting_a_keyword_and_its_tokens(
            "include", "not_str_or_none", raises=DoxhooksTypeError)

        assert self.error.value == self.context.not_str_or_none
