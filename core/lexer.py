"""
First step is to write a lexer. To do this, I will need to use regex to match tokens. 
The lexer matches the code to token types and returns a list.
In python, the "re" module is used.
Types can be stores in an enum class which basically numbers each type to make them more manageable.
The tokens are stored in a dataclass.
"""
import re
from core.data.token_types import *

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.line = 1
        # Token specification contains each token type and the pattern corresponding to it
        self.token_specification = [
            (TokenType.OPEN_BRACE, r'{'),
            (TokenType.CLOSE_BRACE, r'}'),
            (TokenType.OPEN_PARENTHESIS, r'\('),
            (TokenType.CLOSE_PARENTHESIS, r'\)'),
            (TokenType.WHITESPACE, r'[ \t]+'),
            (TokenType.NEWLINE, r'\n'),
            (TokenType.SEMICOLON, r';'),
            (TokenType.ID, r'[a-zA-Z_][a-zA-Z0-9_]*'),
            (TokenType.INT_LITERAL, r'[0-9]+'),
            (TokenType.BIT_COMP, r'~'),
            (TokenType.BIT_SHIFT_LEFT, r'<<'),
            (TokenType.BIT_SHIFT_RIGHT, r'>>'),
            (TokenType.AND, r'&&'),
            (TokenType.OR, r'\|\|'),
            (TokenType.BIT_OR, r'\|'),
            (TokenType.BIT_XOR, r'^'),
            (TokenType.BIT_AND, r'&'),
            (TokenType.MODULO, r'%'),
            (TokenType.EQUAL, r'=='),
            (TokenType.NOT_EQUAL, r'!='),
            (TokenType.LESS_THAN_OR_EQUAL, r'<='),
            (TokenType.LESS_THAN, r'<'),
            (TokenType.GREATER_THAN_OR_EQUAL, r'>='),
            (TokenType.GREATER_THAN, r'>'),
            (TokenType.LOGICAL_NEGATION, r'!'),
            (TokenType.SUBTRACTION, r'-'),
            (TokenType.ADDITION, r'[+]'),
            (TokenType.DIVISION, r'[/]'),
            (TokenType.MULTIPLICATION, r'[*]'),
            ]
        # A dict is used here to differentiate keywords from ID 
        self.keywords = {
            "int": TokenType.INT,
            "return": TokenType.RETURN
        }
        self.tokens = []

    def tokenise(self) -> list:
        # Make a string of all the patterns in the specification
        pattern = "|".join(f'(?P<{tok_type.name}>{regex})' for tok_type, regex in self.token_specification)
        master_pattern = re.compile(pattern)

        # finditer goes through text and finds any matches
        for match in master_pattern.finditer(self.text):

            # match.group() gives the string that was matched
            value = match.group()

            # match.lastgroup gives the type that was matched as a string and TokenType[] turns it back into an Enum (not string)
            type = TokenType[match.lastgroup]
            if type == TokenType.ID and value in self.keywords:
                type = self.keywords[value]
            
            if type == TokenType.NEWLINE:
                self.line += 1
            elif type != TokenType.WHITESPACE:
                self.tokens.append(Token(type=type, value=value, line=self.line))
        
        return self.tokens