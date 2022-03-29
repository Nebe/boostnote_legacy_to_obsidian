from dataclasses import dataclass

from typing import AnyStr, Tuple, Optional, Union, List, Dict, Collection, Type
from typing import NamedTuple  # fpr unpackable dataclasses as in: a, b = unpackable_object

'''
General notes on design of CSON parser:
The following implementation does not support full CSON feature set
because it's main use case is in the convrsion of "legacy Boostnote" notes to Obsidian
and for this purpose this parser suffices completely. See https://github.com/lifthrasiir/cson for all features.

Lack of support for:
1. string literals separated by whitespace are not connected into one string
2. alternative key-value separator "=" is not supported, only ":"
3. so called "verbatim strings" are not supported (delimited by "|" and new line)
4. JSON syntax not supported, especially that implies "," as value separator

DelimitedPolicyMixin
'''

AnyTokenValueType = Union['CompositeTokenValueType', 'LeafTokenValueType']
LeafTokenValueType = Optional[
    Union[
        str,  # string literals
        float,  # num literals
        bool,  # false or true literals
        # date  # some string literals are in fact formatted date representations]
    ]
]


CompositeTokenValueType = Union[
    "CompositeTokenValueType",
    List[AnyTokenValueType],  # list
    Dict[AnyStr, AnyTokenValueType],  # dict
    # a key value pair, will probably be deprecated.
]


@dataclass
class CSON_TokenBase:
    start_index: int  # for debugging
    value: AnyTokenValueType  # no reason to hide it behind an abstract method because of the dynamic nature of python

    # to be re-implemented by the according sub-classes, as close to this base class as possible
    # to reduce code duplication; not raising NotImplemented() and also not using @abstractmethod decorator because
    # it does not have to be implemented in every subclass, but the right implementation should be *accessible*.
    @classmethod
    def consume(cls: Type["CSON_TokenBase"], str_input: AnyStr, start_index: int) -> Optional["ParserResultWrapper"]:
        ...


# TODO: use these types to create double dispatch visitors; add accept method to the CSON_TokenBase.
# as opposed to C++, no need to override this accept method in each derived class, because
# real type of self is always known.
class CSON_LeafToken(CSON_TokenBase):
    def __init__(self, start_index: int, value_: Optional[LeafTokenValueType]):
        super(CSON_LeafToken, self).__init__(start_index=start_index, value=value_)


class CSON_NameToken(CSON_TokenBase):
    def __init__(self, start_index: int, value_: AnyStr):
        super(CSON_NameToken, self).__init__(start_index=start_index, value=value_)


# 1. codifies the fact, that the inheriting CLASS posses the _DELIMITERS attribute
#    accessible through cls.delimiters() on the class itself.
# 2. provides consume() method suitable for delimited tokens, both composite and leaf.
class DelimitedPolicyMixin:
    # important NOT to name such class attributes as private (__DELIMITERS, leads to name mangling),
    # because it will not even be accessible on the class itself
    _DELIMITERS: Tuple[AnyStr, AnyStr] = None

    @classmethod
    def delimiters(cls):
        if cls._DELIMITERS is None:
            raise NotImplementedError(f"{cls} must define __DELIMITERS since it inherits from DelimitersMixin.")
        return cls._DELIMITERS

    @classmethod
    def consume(cls, *args, **kwargs):
        return consume_delimited_generic(cls, *args, **kwargs)


class CSON_StringBase(DelimitedPolicyMixin, CSON_LeafToken):

    def __init__(self, start_index: int, value_: AnyStr = ""):
        super(CSON_StringBase, self).__init__(start_index=start_index, value_=value_)

    def consume_next_sub_element(self, str_input, start_index):
        # if backslash then consume it and  the char after it as well, to avoid it being recognized as a delimiter.
        if str_input[start_index] == "\\":
            self.value += str_input[start_index:start_index + 2]
            return start_index + 2
        # consume just one char
        self.value += str_input[start_index]
        return start_index + 1


class ParserResultWrapper(NamedTuple):
    # un-packable tuple, the following attributes are instance members, not class member as it may seem.
    next_input_index: int = 0
    parsed_token: CSON_TokenBase = None


class CSON_StringToken(CSON_StringBase):
    _DELIMITERS = ("\"", "\"")


class CSON_MultiLineStringToken(CSON_StringBase):
    _DELIMITERS = ("\'\'\'", "\'\'\'")


def match_ignore_alpha(str_input: AnyStr, index: int) -> Optional[int]:
    if index < len(str_input) and str_input[index].isalpha():
        return index + 1

    return None


# consumes any name, in CSON files can only appear as a dict key.
# examples: a, ab1, var_name
def consume_name(str_input, start_index):

    i = start_index
    # 1. key name token must start with a character
    if not (i := match_ignore_alpha(str_input, i)):
        return

    # at this point one char was processed and we already have a key name or unquoted literal token
    # 2. iterate over the rest of chars and nums
    input_len = len(str_input)
    while i < input_len and (str_input[i].isalnum() or str_input[i] == "_"):
        i += 1

    name = str_input[start_index:i]

    # simple ugly check against the only keywords in CSON
    if name in ["false", "true"]:
        return None

    return ParserResultWrapper(i, CSON_NameToken(start_index, name))


# while not technically a structural type (not inheriting from typing.Protocol and also has actual base classes)
# is used here for the sake of annotation, because there is no proper way to denote it otherwise.
class DelimitedToken(DelimitedPolicyMixin, CSON_TokenBase):
    ...


# delimiters and token_type arguments will be bound before use
# works for leaf as well as composite token types, because the actual consume operation is abstracted away
def consume_delimited_generic(token_type: type(DelimitedToken), str_input: AnyStr, start_index: int):
    right, left = token_type.delimiters()
    if (index := match_ignore_text(str_input, start_index, right)) is not None:
        parser_result = consume_until_end_seq(str_input, index, left, token_type)
        return parser_result

    return None


# tag class for all composites
class CSON_TokenCompositeBase(DelimitedPolicyMixin, CSON_TokenBase):
    _SUBTOKEN_TYPES: Collection[CSON_TokenBase] = None  # will be assigned later on to avoid forward declaration problem

    def consume_next_sub_element(self, str_input, start_index):
        raise NotImplementedError()


class CSON_DictToken(CSON_TokenCompositeBase):
    _DELIMITERS = ("{", "}")
    KEY_VALUE_INFIX_DELIMITER = ":"

    def __init__(self, start_index):
        super(CSON_DictToken, self).__init__(start_index=start_index,
                                             value=dict())

    def consume_next_sub_element(self, str_input, start_index):
        start_index = ignore_whitespace(str_input, start_index)
        result = self._consume_key_value(str_input, start_index)
        if result is not None:
            next_index, key_, value_ = result
            self.value[key_.value] = value_.value

            next_index = ignore_whitespace(str_input, next_index)
            return next_index

        return None

    # for the document itself, since it is a dictionary without delimiters
    @staticmethod
    def consume_document(str_input):
        start_index = 0
        document = CSON_DictToken(start_index)  # expects the token to be default initialisable
        j = ignore_whitespace(str_input, start_index)

        input_length = len(str_input)
        if not input_length:
            return document.value

        while j < input_length:
            j = document.consume_next_sub_element(str_input, j)

        return document.value

    def _consume_key_value(self, str_input: AnyStr, start_index: int) -> Optional[tuple[int, AnyStr, AnyTokenValueType]]:

        i, name_token = consume_name(str_input, start_index)

        i = ignore_whitespace(str_input, i)
        if i == len(str_input):
            return

        # it will only turn out to be a key name token if it is followed by ":"
        if str_input[i] == self.KEY_VALUE_INFIX_DELIMITER:
            # no need to check whether the key is empty or not - it contains at least one character (see comment 1.)
            i, value_token = cson_gen_next_token(str_input, i + 1, self._SUBTOKEN_TYPES)

            return i, name_token, value_token

        return None


class CSON_ListToken(CSON_TokenCompositeBase):
    _DELIMITERS = ("[", "]")
    _SUB_TOKEN_FACTORIES = ()

    def __init__(self, start_index):
        super(CSON_ListToken, self).__init__(start_index=start_index,
                                             value=list()
                                             )

    def _add_subtoken(self, token_: CSON_TokenBase):
        self.value.append(token_)

    def consume_next_sub_element(self, str_input, start_index):
        if parser_result := cson_gen_next_token(str_input, start_index, self._SUBTOKEN_TYPES):
            self._add_subtoken(parser_result.parsed_token.value)
            next_index = ignore_whitespace(str_input, parser_result.next_input_index)
            return next_index

        return None


class CSON_NumberToken(CSON_LeafToken):
    def __init__(self, start_index: int, value_: float):
        super(CSON_NumberToken, self).__init__(start_index=start_index, value_=value_)

    @staticmethod
    def consume(str_input: AnyStr, start_index: int):
        # all this code coudl easely be substituted by a short regex..
        index = start_index
        input_length = len(str_input)
        # 1. check whether its a negative number or not
        if str_input[index] == "-":
            index += 1

        # 2. it must start with a number, CSON/JSON number literals are quite different from python's
        if index < input_length and str_input[index].isnumeric():
            index += 1
        else:
            return None

        # 3. consume all following digits
        while index < input_length and str_input[index].isnumeric():
            index += 1
        # 4. consume dot if present
        if index < input_length and str_input[index] == ".":
            index += 1
            index_after_dot = index
            # 5. at least one number must follow the dot
            while index < input_length and str_input[index].isnumeric():
                index += 1
            else:
                # 6 raise exception if no digits followed the dot
                if index == index_after_dot:
                    raise BrokenTokenError(start_index, f"A number cannot end with a dot: {str_input[start_index:index]}")

        # if index is pointing at any other char then this is not a legal number,
        # i.e. 1.23f and 1.23% are not cson numbers
        if index < input_length and not (str_input[index].isspace() or str_input[index] in ["]", "}"]):
            raise BrokenTokenError(start_index, f"A number is followed by unexpected char: {str_input[start_index:index+1]}")
        try:
            # 7. actually cast it to float
            parsed_float = float(str_input[start_index:index])
        except ValueError as e:
            # should never happen, was unable to parse for some reason
            raise e
        else:
            # the only success return, executed if no exception
            return ParserResultWrapper(index, CSON_NumberToken(index, parsed_float))


class CSON_BooleanToken(CSON_LeafToken):
    def __init__(self, start_index: int, value_: bool = None):
        super(CSON_BooleanToken, self).__init__(start_index=start_index,
                                                value_=value_)

    @staticmethod
    def consume(str_input: AnyStr, start_index: int) -> Optional[ParserResultWrapper]:
        values = {"false": False, "true": True}
        for literal, bool_value in values.items():
            # 1. key name token must start with a character
            if str_input[start_index] != literal[0]:
                continue

            if index_after_literal := match_ignore_text(str_input, start_index, literal):
                return ParserResultWrapper(index_after_literal, CSON_BooleanToken(start_index, bool_value))

        return None


# if str_input[start_index:] starts with text_to_match -> return the index right after text_to_match
# otherwise return None
def match_ignore_text(str_input: AnyStr, start_index: int, text_to_match: AnyStr) -> Optional[int]:
    index_after_seq = start_index + len(text_to_match)
    if index_after_seq <= len(str_input) and str_input[start_index:index_after_seq] == text_to_match:
        return index_after_seq
    # start_index does not point at the start of a token of type token_type.
    return None


# generates the next token.
def cson_gen_next_token(str_input: AnyStr, i: int, subtoken_types: Collection[CSON_TokenBase]) \
        -> Optional[ParserResultWrapper]:
    i = ignore_whitespace(str_input, i)

    if i >= len(str_input):
        # EOF too early
        raise TextEndedPrematurelyError()

    for subtoken_type in subtoken_types:
        if result := subtoken_type.consume(str_input, i):
            return result

    raise UnknownTokenError(i)


def ignore_whitespace(str_input, current_index):
    input_len = len(str_input)
    while current_index < input_len and str_input[current_index].isspace():
        current_index += 1
    return current_index


# assumes that the right delimiter was already encountered and the start index point at first index after it
# this is why it is safe to create the new token at the start of the function.
def consume_until_end_seq(str_input, start_index, end_seq, token_type: type(CSON_TokenBase)):
    new_token = token_type(start_index)  # expects the token to be default initialisable
    seq_len = len(end_seq)
    delimiter_reached = False
    j = start_index
    # are there enough characters left in str_input for comparison
    max_comparison_index = len(str_input) - seq_len
    while j <= max_comparison_index:
        # are next seq_len characters equal to the stop_char_seq?
        if match_ignore_text(str_input, j, end_seq):
            delimiter_reached = True
            break
        if not (j := new_token.consume_next_sub_element(str_input, j)):
            raise BrokenTokenError(start_index, f"{token_type}, consume() failed from: {str_input[start_index:30]} ...")

    if not delimiter_reached:
        raise DelimiterNotFoundError(end_seq, start_index)

    next_char_index = j + seq_len
    return ParserResultWrapper(next_char_index, new_token)


def parse_cson(str_input: AnyStr) -> dict:
    return CSON_DictToken.consume_document(str_input)


# solution to the forward decl. problem
def init():
    # practically all token types except CSON_NameToken,
    # which is handled separately and appears only in dictionaries as the key.
    CSON_TokenCompositeBase._SUBTOKEN_TYPES = [CSON_ListToken, CSON_DictToken,
                                               CSON_StringToken, CSON_MultiLineStringToken,
                                               CSON_NumberToken, CSON_BooleanToken]


init()


class DelimiterNotFoundError(Exception):
    """Exception raised when an expected character is not found.

    stop_char: missing char
    message: explanation of the error
    """

    def __init__(self, stop_char, index_from, message="Did not hit \"{}\". Consumed from {}."):
        self.index_from = index_from
        self.stop_char = stop_char
        self.message = message.format(stop_char, index_from)
        super().__init__(self.message)


class TextEndedPrematurelyError(Exception):
    pass


# raised if all token's consume methods fail (without raising BrokenTokenError)
class UnknownTokenError(Exception):
    def __init__(self, index):
        self.index = index
        self.message = "Token type could not be detected: index {}.".format(index)
        super().__init__(self.message)


# raised for any piece of input that first satisfies the match criteria but then turns out to be corrupt
# i.e "1.23f" starts as a number, but ends with "f" which is nto supported in CSON.
class BrokenTokenError(Exception):
    def __init__(self, index, message):
        self.index = index
        self.message = "Index {}: ".format(index) + message
        super().__init__(self.message)
