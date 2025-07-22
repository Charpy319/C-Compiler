from dataclasses import dataclass
from enum import Enum, auto

# TokenType class stores all the available token types
class TokenType(Enum):
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    SEMICOLON = auto()
    INT = auto()
    RETURN = auto()
    ID = auto()
    INT_LITERAL = auto()
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
    COMMA = auto()
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

# Token dataclass defines what is in each token, like a struct in C
@dataclass
class Token:
    type: TokenType
    value: str
    line: int