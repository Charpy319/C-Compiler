from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

# TokenType class stores all the available token types
class TokenType(Enum):
    # Delimeters
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    SEMICOLON = auto()
    COLON = auto()
    QUESTION_MARK = auto()
    DOT = auto()
    SINGLE_QUOTE = auto()
    DOUBLE_QUOTE = auto()
    COMMA = auto()

    # Keywords/ID
    INT = auto()
    CHAR = auto()
    FLOAT = auto()
    DOUBLE = auto()
    VOID = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    DO = auto()
    BREAK = auto()
    CONTINUE = auto()
    ID = auto()

    # Literals
    INT_LITERAL = auto()
    STRING_LIT = auto()
    FLOAT_LIT = auto()
    DOUBLE_LIT = auto()
    CHAR_LIT = auto()

    # Operations
    BIT_COMP = auto()
    ASSIGN_ADD = auto()
    ASSIGN_SUB = auto()
    ASSIGN_MULT = auto()
    ASSIGN_DIV = auto()
    ASSIGN_MOD = auto()
    ASSIGN_LEFT_SHIFT = auto()
    ASSIGN_RIGHT_SHIFT = auto()
    ASSIGN_BIT_AND = auto()
    ASSIGN_BIT_OR = auto()
    ASSIGN_BIT_XOR = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    BIT_SHIFT_LEFT = auto()
    BIT_SHIFT_RIGHT = auto()
    AND = auto()
    OR = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_AND = auto()
    MODULO = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN_OR_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN_OR_EQUAL = auto()
    GREATER_THAN = auto()
    LOGICAL_NEGATION = auto()
    SUBTRACTION = auto()
    ADDITION = auto()
    DIVISION = auto()
    MULTIPLICATION = auto()
    ASSIGNMENT = auto()

    # Error
    ERROR = auto()

# Token dataclass defines what is in each token, like a struct in C
@dataclass
class Token:
    type: TokenType
    line: int
    value: Optional[str] = None