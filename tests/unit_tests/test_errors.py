from doxhooks.errors import (
    DoxhooksError, DoxhooksForbiddenLookupError, DoxhooksLookupError,
    DoxhooksTypeError, DoxhooksValueError)
from pytest import mark


class BaseTestError:
    def given_an_internal_error(self, error):
        self.error = error

    def when_reading_the_error_message(self):
        self.error_message = str(self.error)

    def when_investigating_the_value_that_caused_the_error(self):
        self.cause = self.error.value

    def then_the_cause_is_found(self, cause):
        assert self.cause == cause


class TestError(BaseTestError):
    @mark.parametrize(
        "args, message", [
            (("test", "message", 1, {}), "test message 1 {}"),
        ])
    def test_an_error_message_is_formatted_for_the_user(self, args, message):
        self.given_an_internal_error(DoxhooksError(*args))

        self.when_reading_the_error_message()

        # then the message is a nicely formatted string suitable for
        # the user to read.
        assert self.error_message == message


class TestLookupError(BaseTestError):
    @mark.parametrize(
        "lookup_error, message", [
            (DoxhooksLookupError(1, [], "the list"),
                "Cannot find 1 in the list."),
            (DoxhooksLookupError("my_key", {}, "the dict"),
                "Cannot find 'my_key' in the dict."),
        ])
    def test_a_lookup_error_message_has_the_key_and_container(
            self, lookup_error, message):
        self.given_an_internal_error(lookup_error)

        self.when_reading_the_error_message()

        # then the error message has the key and a description of the
        # container.
        assert self.error_message == message


class TestForbiddenLookupError(BaseTestError):
    @mark.parametrize(
        "forbidden_lookup_error, message", [
            (DoxhooksForbiddenLookupError("_private_key", {}, "the dict"),
                "Forbidden to look up '_private_key' in the dict."),
        ])
    def test_a_forbidden_lookup_error_message_has_the_key_and_container(
            self, forbidden_lookup_error, message):
        self.given_an_internal_error(forbidden_lookup_error)

        self.when_reading_the_error_message()

        # then the error message has the key and a description of the
        # container.
        assert self.error_message == message


class TestTypeError(BaseTestError):
    @mark.parametrize(
        "type_error, message", [
            (DoxhooksTypeError(1, "identifier", "str or None"),
                "Bad type for `identifier`: int. (Should be str or None.)"),
            (DoxhooksTypeError(1, "identifier", str),
                "Bad type for `identifier`: int. (Should be str.)"),
            (DoxhooksTypeError(1, "identifier", (str, type(None))),
                "Bad type for `identifier`: int. (Should be str, NoneType.)"),
            (DoxhooksTypeError(1, "identifier", ()),
                "Bad type for `identifier`: int. (Should be 'no type'.)"),
        ])
    def test_a_type_error_message_has_the_identifier_and_type_and_a_hint(
            self, type_error, message):
        self.given_an_internal_error(type_error)

        self.when_reading_the_error_message()

        # then the error message has the identifier, type and a hint.
        assert self.error_message == message

    def test_a_type_error_returns_the_value_that_caused_the_error(self):
        bad_type_of_value = 1
        self.given_an_internal_error(
            DoxhooksTypeError(bad_type_of_value, "identifier", "str or None"))

        self.when_investigating_the_value_that_caused_the_error()

        self.then_the_cause_is_found(bad_type_of_value)


class TestValueError(BaseTestError):
    @mark.parametrize(
        "value_error, message", [
            (DoxhooksValueError(1, "identifier", "0 or 2"),
                "Bad value for `identifier`: 1. (Should be 0 or 2.)"),
            (DoxhooksValueError(1, "identifier"),
                "Bad value for `identifier`: 1."),
        ])
    def test_a_value_error_message_has_the_identifier_and_value_and_a_hint(
            self, value_error, message):
        self.given_an_internal_error(value_error)

        self.when_reading_the_error_message()

        # then the error message has the identifier, value and an
        # optional hint.
        assert self.error_message == message

    def test_a_value_error_returns_the_value_that_caused_the_error(self):
        bad_value = 1
        self.given_an_internal_error(
            DoxhooksValueError(bad_value, "bad_value", "0 or 2"))

        self.when_investigating_the_value_that_caused_the_error()

        self.then_the_cause_is_found(bad_value)
