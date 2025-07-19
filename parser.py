"""
The next step is to make the parser, which builds an abstract syntax tree from the list of tokens.
The root of the tree will be the entrie program and its children will be the different parts of the program.
For this example, the tree will look like this:

Program -> Function(main) -> Return -> Value

Different dataclasses will be used to establish the relationship between each node type.
"""
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

@dataclass
class Exp:
    value: int

@dataclass
class Statement:
    expression: Exp

@dataclass
class Function:
    name: str
    body: Statement

@dataclass
class Program:
    function: Function

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self) -> str:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def check_type(self, expected_type: TokenType) -> str:
        tok = self.peek()
        if tok.type.name == expected_type:
            self.pos += 1
            return tok.value
        else:
            raise SyntaxError(f"Expected {expected_type}, got {tok.type.name}")
        
    def parse_exp(self) -> Exp:
        tok = self.check_type(TokenType.INT_LITERAL.name)
        return Exp(value=int(tok))
    
    def parse_statement(self) -> Statement:
        self.check_type(TokenType.RETURN.name)
        tok = self.parse_exp()
        self.check_type(TokenType.SEMICOLON.name)
        return Statement(expression=tok)
    
    def parse_function(self) -> Function:
        self.check_type(TokenType.INT.name)
        name = self.check_type(TokenType.ID.name)
        self.check_type(TokenType.OPEN_PARENTHESIS.name)
        self.check_type(TokenType.CLOSE_PARENTHESIS.name)
        self.check_type(TokenType.OPEN_BRACE.name)
        body = self.parse_statement()
        self.check_type(TokenType.CLOSE_BRACE.name)
        return Function(name=name, body=body)
    
    def parse_program(self) -> Program:
        func = self.parse_function()
        return Program(function=func)