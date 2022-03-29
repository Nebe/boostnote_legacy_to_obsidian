from typing import  Any, Type, AnyStr, Dict, Union, Protocol

import pytest
from cson_parser import CSON_NumberToken, CSON_BooleanToken, CSON_DictToken, CSON_ListToken, \
    CSON_MultiLineStringToken, CSON_NameToken, CSON_StringToken, UnknownTokenError, BrokenTokenError, \
    DelimiterNotFoundError
# Uncomment for debugging in the console with pdb;start not in debug mode;
# type "b file.py:line_number" to set a pointer; type "help" for more
# import pdb
# pdb.set_trace()

# Code from "Python Object-Oriented Programming" 2021 Lott, Phillips (Packt)
# Comments from me.
#
# All it takes to test something is: test function, pre/post actions, mock ups.
#
# Important: call with "python -m pytest -s tests\column_detection_test.py"
# -s flag to disable console output suppression.
#
# This is my pytest showcase module.
# 1.  Any function that starts with "test" will be called.
# 2.  Following setup/teardown levels are supported by pytest(see examples below):
#         module level -> setup_module, teardown_module -> once per module file
#         class level -> setup_class, teardown_class  -> once per class
#         class-method level -> setup_method, teardown_method -> once per each test* method
#     This implies that functions are to be encapsulated into a class only if they have
#     common class AND method setup/teardown functionality.
# 3.  A fixture function returns the mocked-up object;
#     pytest injects the return value into the test function that uses it.
#     Dependency Injection is used by pytest so no manual wiring is needed.
#     The pytest runtime looks for functions with the @fixture decorator that match the parameter name.
# 3.1 A Fixture can be implemented as a generator.
#     Important: as opposed to simple fixtures - the generator itself is injected and has to be called manually.
#     Then it can also run cleanup code after each test is run,
#     written after the "yield".  This provides the equivalent of a teardown method on a per-fixture basis
#     but the fixture is a stateful object then - mock ups are easier to handle.
#
# TODO: Free test-functions are also supported but i am not sure yet how to define setup/teardown for them


#
# # Example from the book
#
# class BaseTest:
#
#     @classmethod
#     def setup_class(cls: Type["BaseTest"]) -> None:
#         print(f"setting up CLASS {cls.__name__}")
#
#     @classmethod
#     def teardown_class(cls: Type["BaseTest"]) -> None:
#         print(f"tearing down CLASS {cls.__name__}\n")
#
#     def setup_method(self, method: Callable[[], None]) -> None:
#         print(f"setting up METHOD {method.__name__}")
#
#     def teardown_method(self, method: Callable[[], None]) -> None:
#         print(f"tearing down METHOD {method.__name__}")
#
#
# class TestClass1(BaseTest):
#     def test_method_1(self) -> None:
#         print("RUNNING METHOD 1-1")
#
#     def test_method_2(self) -> None:
#         print("RUNNING METHOD 1-2")
#
#
# class TestClass2(BaseTest):
#     def test_method_1(self) -> None:
#         print("RUNNING METHOD 2-1")
#
#     def test_method_2(self) -> None:
#         print("RUNNING METHOD 2-2")


def setup_module(module: Any) -> None:
    print(f"Testing began for module {module.__name__}.")


def teardown_module(module: Any) -> None:
    print(f"Testing ended for module {module.__name__}")


@pytest.fixture
def cases_numbers():
    # some of these are proper python floats, but not CSON numbers.
    return {"Fail": [".", ".-", ".1"],
            "Exception": ["1.23f", "-0.", "-.0", "0.", "-", "-."],
            "Success": [("-1.23 \n", -1.23), ("123", 123)]}


@pytest.fixture
def cases_strings():
    return {"Fail": ["", "a\""],  # 1. empty string contains no string; 2. does not start with a string delimiter
            "Exception": ["\"", "\"a"],  # delimiters are absent
            # empty string, string contains a number literal which is not to be parsed
            "Success": [("\"\"", ""), ("\"0.\"", "0."), ("\" abc \"", " abc ")]}


def test_number_consume(cases_numbers):
    print("1. Not-numbers fail by returning None.")
    for number_str in cases_numbers["Fail"]:
        assert CSON_NumberToken.consume(number_str, 0) is None

    print("2. Not-numbers which start as numbers raise BrokenTokenError.")
    with pytest.raises(BrokenTokenError):
        for number_str in cases_numbers["Exception"]:
            result = CSON_NumberToken.consume(number_str, 0)
            raise RuntimeError(f"Number {number_str} did not throw expected exception!Result: {result}")

    print("3. Legal CSON Numbers are successfully parsed.")
    for number_str, expected_result in cases_numbers["Success"]:
        assert CSON_NumberToken.consume(number_str, 0).parsed_token.value == expected_result


def test_string_consume(cases_strings):
    print("1. Not-strings fail by returning None.")
    for string in cases_strings["Fail"]:
        assert CSON_StringToken.consume(string, 0) is None

    print("2. Not-strings which falsely  start as strings raise BrokenTokenError.")
    with pytest.raises(DelimiterNotFoundError):
        for string in cases_strings["Exception"]:
            result = CSON_StringToken.consume(string, 0)
            raise RuntimeError(f"String {string} did not throw expected exception! Result: {result}")

    print("3. Legal CSON strings are successfully parsed.")
    for string, expected_result in cases_strings["Success"]:
        assert CSON_StringToken.consume(string, 0).parsed_token.value == expected_result

