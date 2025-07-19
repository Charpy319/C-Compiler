"""
The next step is to make the parser, which builds an abstract syntax tree from the list of tokens.
The root of the tree will be the entrie program and its children will be the different parts of the program.
For this example, the tree will look like this:

Program -> Function(main) -> Return -> Value

Different dataclasses will be used to establish the relationship between each node type.
"""
from dataclasses import dataclass
from typing import Optional, Union
from lexer import Token, TokenType

# The dataclasses below represent the different types of nodes of the AST
@dataclass
class IntLiteral:
    value: int

@dataclass
class UnOp:
    operator: str
    operand: 'Exp'

@dataclass
class AddSub:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class MultDiv:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class Parenthesis:
    exp: 'Exp'

# Union means that it can be of any of the types in the []
Exp = Union[AddSub, MultDiv, Parenthesis, UnOp, IntLiteral]

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
    
    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def check_type(self, *expected_type: TokenType) -> Token:
        for e in expected_type:
            tok = self.peek()
            if tok.type == e:
                self.pos += 1
                return tok
        raise SyntaxError(f"Expected {expected_type}, got '{tok.value}' {tok.type} on line {tok.line}")
    
    # Builds AST from the program node down
    def parse_fact(self) -> Exp:
        tok = self.check_type(
            TokenType.OPEN_PARENTHESIS,
            TokenType.INT_LITERAL,
            TokenType.SUBTRACTION, 
            TokenType.BITWISE_COMPLEMENT, 
            TokenType.LOGICAL_NEGATION
        )
        if tok.type == TokenType.OPEN_PARENTHESIS:
            tok = self.parse_exp()
            self.check_type(TokenType.CLOSE_PARENTHESIS)
            return Parenthesis(exp=tok)
        
        elif tok.type == TokenType.INT_LITERAL:
            return IntLiteral(value=int(tok.value))
        
        else:
            inner_exp = self.parse_exp()
            return UnOp(operator=tok.value, operand=inner_exp)

    def parse_term(self) -> Exp:
        fact = self.parse_fact()
        next = self.peek()
        while next.type == TokenType.MULTIPLICATION or next.type == TokenType.DIVISION:
            op = self.check_type(TokenType.MULTIPLICATION, TokenType.DIVISION)
            next_fact = self.parse_fact()
            fact = MultDiv(operator=op.value, operand1=fact, operand2=next_fact)
            next = self.peek()
        return fact

    def parse_exp(self) -> Exp:
        term = self.parse_term()
        next = self.peek()
        while next.type == TokenType.ADDITION or next.type == TokenType.SUBTRACTION:
            op = self.check_type(TokenType.ADDITION, TokenType.SUBTRACTION)
            next_term = self.parse_term()
            term = AddSub(operator=op.value, operand1=term, operand2=next_term)
            next = self.peek()
        return term
    
    def parse_statement(self) -> Statement:
        self.check_type(TokenType.RETURN)
        exp = self.parse_exp()
        self.check_type(TokenType.SEMICOLON)
        return Statement(expression=exp)
    
    def parse_function(self) -> Function:
        self.check_type(TokenType.INT)
        name = self.check_type(TokenType.ID)
        self.check_type(TokenType.OPEN_PARENTHESIS)
        self.check_type(TokenType.CLOSE_PARENTHESIS)
        self.check_type(TokenType.OPEN_BRACE)
        body = self.parse_statement()
        self.check_type(TokenType.CLOSE_BRACE)
        return Function(name=name.value, body=body)
    
    def parse_program(self) -> Program:
        func = self.parse_function()
        return Program(function=func)