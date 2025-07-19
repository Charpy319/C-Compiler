"""
First step is to write a lexer. To do this, I will need to use regex to match tokens. 
The lexer matches the code to token types and returns a list.
In python, the "re" module is used.
Types can be stores in an enum class which basically numbers each type to make them more manageable.
The tokens are stored in a dataclass.
"""
import re
from dataclasses import dataclass
from enum import Enum, auto

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

@dataclass
class Token:
    type: TokenType
    value: str
    line: int

with open("return.c", "r") as file:
    text = file.read()

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.line = 1
        self.token_specification = [
            (TokenType.OPEN_BRACE, r'{'),
            (TokenType.CLOSE_BRACE, r'}'),
            (TokenType.OPEN_PARENTHESIS, r'\('),
            (TokenType.CLOSE_PARENTHESIS, r'\)'),
            (TokenType.WHITESPACE, r'[ \t]+'),
            (TokenType.NEWLINE, r'\n'),
            (TokenType.SEMICOLON, r';'),
            (TokenType.ID, r'[a-zA-Z_][a-zA-Z0-9_]*'),
            (TokenType.INT_LITERAL, r'[0-9]+')
            ]
        self.keywords = {
            "int": TokenType.INT,
            "return": TokenType.RETURN
        }
        self.tokens = []

    def tokenise(self) -> list:
        pattern = "|".join(f'(?P<{tok_type.name}>{regex})' for tok_type, regex in self.token_specification)
        master_pattern = re.compile(pattern)

        for match in master_pattern.finditer(self.text):
            value = match.group()
            type = TokenType[match.lastgroup]
            if type == TokenType.ID and value in self.keywords:
                type = self.keywords[value]
            
            if type == TokenType.NEWLINE:
                self.line += 1
            elif type != TokenType.WHITESPACE:
                self.tokens.append(Token(type=type, value=value, line=self.line))
        
        return self.tokens