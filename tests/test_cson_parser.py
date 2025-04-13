from typing import  Any, Type, AnyStr, Dict, Union, Protocol

import pytest
from cson_parser import CSON_NumberToken, CSON_BooleanToken, CSON_DictToken, CSON_ListToken, \
    CSON_MultiLineStringToken, CSON_NameToken, CSON_StringToken, UnknownTokenError, BrokenTokenError, \
    DelimiterNotFoundError, CSON_TokenBase

# Uncomment for debugging in the console with pdb;start not in debug mode;
# type "b file.py:line_number" to set a pointer; type "help" for more
# import pdb
# pdb.set_trace()

# Testing knowledge from "Python Object-Oriented Programming" 2021 Lott, Phillips (Packt)
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


def setup_module(module: Any) -> None:
    print(f"\nTesting began for module {module.__name__}.")


def teardown_module(module: Any) -> None:
    print(f"\nTesting ended for module {module.__name__}")


@pytest.fixture
def cases_numbers():
    # some of these are proper python floats, but not CSON numbers.
    return {"Fail": ["", ".", "-", ".-", "-.0", ".1"],
            "Exception": [("1.23f", BrokenTokenError), ("-0.", BrokenTokenError), ("0.", BrokenTokenError)],
            "Success": [("-1.23 \n", -1.23), ("123", 123)]}


@pytest.fixture
def cases_strings():
    return {"Fail": ["", "a\""],  # 1. empty string contains no string; 2. does not start with a string delimiter
            "Exception": [("\"", DelimiterNotFoundError), ("\"a", DelimiterNotFoundError)],  # delimiters are absent
            # empty string, string contains a number literal which is not to be parsed, string with whitespace
            "Success": [("\"\"", ""), ("\"0.\"", "0."), ("\" abc \"", " abc ")]}


@pytest.fixture
def cases_list():
    # lists and dicts (as the only composite types) contain other tokens
    #  and can not fail except their sub-tokens have failed.

    # 1. comma char fails inside the list, since it is not valid pure CSON;
    # 2. name cannot be part of a list.
    # 3. exceptions of sub-tokens propagate
    # 4. the right delimiter is missing
    return {"Exception": [("[\"\" , 10]", UnknownTokenError),
                          ("[\"string\" name]", UnknownTokenError),
                          ("[\"price\" -5.]", BrokenTokenError),
                          ("[\"price\" ", DelimiterNotFoundError)],
            # 1. a basic list with two sub-tokens
            # 2. empty list
            "Success": [("[\"\" 5]", ["", 5.0]),
                        ("[]", [])]}

@pytest.fixture
def cases_dict():
    # lists and dicts (as the only composite types) contain other tokens
    #  and can not fail except their sub-tokens have failed.

    # 1. comma char fails inside the list, since it is not valid pure CSON;
    # 2. name cannot be part of a list.
    # 3. exceptions of sub-tokens propagate
    # 4. the right delimiter is missing
    return {"Exception": [("{\"\" , 10}", BrokenTokenError),
                          ("{ price: 5. }", BrokenTokenError),
                          ("{ price: 5 ", DelimiterNotFoundError)],
            # 1. a basic list with two sub-tokens
            # 2. empty list
            # "Success": [("[\"\" 5]", ["", 5.0]),
            #            ("[]", [])]
            }


def generic_token_test_routine(fixture: Dict, token_type: Type[CSON_TokenBase], what: str):
    print(f"\nCSON parser general token test routine: parsing {what} tokens of type {token_type}")
    if "Fail" in fixture:
        print(f"1. Performing fail tests for {what}s.")
        for input_str in fixture["Fail"]:
            assert token_type.consume(input_str, 0) is None
    else:
        print(f"1. Fail test cases are not provided.")

    if "Exception" in fixture:
        print(f"2. Performing exception tests for {what}s.")
        for input_str, exception_type in fixture["Exception"]:
            # rasies Failed exception if the expected exception was not raised
            with pytest.raises(exception_type):
                token_type.consume(input_str, 0)
                # raise RuntimeError(f"{what} {input_str} did not throw expected exception!Result: {result}")
    else:
        print(f"2. Exception test cases are not provided.")

    if "Success" in fixture:
        print(f"2. Performing success tests for {what}s.")
        for input_str, expected_result in fixture["Success"]:
            assert token_type.consume(input_str, 0).parsed_token.value == expected_result
    else:
        print(f"3. Success test cases are not provided.")


# self-registering test functions for each token type follow:
def test_number_consume(cases_numbers):
    generic_token_test_routine(cases_numbers, CSON_NumberToken, "number")


def test_string_consume(cases_strings):
    generic_token_test_routine(cases_strings, CSON_StringToken, "string")


def test_list_consume(cases_list):
    generic_token_test_routine(cases_list, CSON_ListToken, "list")


def test_dict_consume(cases_dict):
    generic_token_test_routine(cases_dict, CSON_DictToken, "dict")
