import io

from pytest import fixture


class _FakeOutputFile(io.StringIO):
    def close(self):
        self.contents = self.getvalue()
        super().close()


@fixture
def fake_output_file():
    return _FakeOutputFile()


type_example_values = {
    "none": (None,),
    "callable": (lambda: None,),

    "bool": (True, False),
    "digit_int": (0, 2,),
    "float": (0.0, 1.2,),

    "bytes": (b"", b"bytes"),
    "str": ("", "string"),

    "list": ([], [None]),
    "tuple": ((), (None,)),

    "dict": ({}, {None: None}),
    "set": (set(), {None}),
}

basic_types = set([type_name for type_name in type_example_values])


class TypeSets:
    int = {"digit_int", "bool"}
    # number = int | {"float"}
    # digits = {"digit_int", "float"}
    # sequence = {"bytes", "str", "list", "tuple"}
    # iterable = sequence | {"dict", "set"}
    # subscriptable = sequence | {"dict"}
    # hashable = basic_types - {"list", "dict", "set"}


for type_name in basic_types:
    setattr(TypeSets, type_name, {type_name})


def values_not_from_types(*type_names):
    excluded_basic_types = [getattr(TypeSets, name) for name in type_names]
    remaining_basic_types = basic_types.difference(*excluded_basic_types)
    example_values = []
    for basic_type in remaining_basic_types:
        example_values.extend(type_example_values[basic_type])
    return example_values


@fixture(params=values_not_from_types("int", "none"))
def not_int_or_none(request):
    return request.param


@fixture(params=values_not_from_types("str"))
def not_str(request):
    return request.param
