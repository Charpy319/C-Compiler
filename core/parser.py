"""
The next step is to make the parser, which builds an abstract syntax tree from the list of tokens.
The root of the tree will be the entrie program and its children will be the different parts of the program.
For this example, the tree will look like this:

Program -> Function(main) -> Return -> Value

Different dataclasses will be used to establish the relationship between each node type.
"""
from typing import Optional
from core.data.token_types import *
from core.data.nodes import *

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
            TokenType.BIT_COMP, 
            TokenType.LOGICAL_NEGATION
        )
        if tok.type == TokenType.OPEN_PARENTHESIS:
            tok = self.parse_and()
            self.check_type(TokenType.CLOSE_PARENTHESIS)
            return Parenthesis(exp=tok)
        
        elif tok.type == TokenType.INT_LITERAL:
            return IntLiteral(value=int(tok.value))
        
        elif (
            tok.type == TokenType.BIT_COMP
            or tok.type == TokenType.SUBTRACTION
            or tok.type == TokenType.LOGICAL_NEGATION
        ):
            inner_exp = self.parse_fact()
            return UnOp(operator=tok.value, operand=inner_exp)

    def parse_term(self) -> Exp:
        fact = self.parse_fact()
        next = self.peek()
        while (
            next.type == TokenType.MULTIPLICATION
            or next.type == TokenType.DIVISION
            or next.type == TokenType.MODULO
            ):
            op = self.check_type(TokenType.MULTIPLICATION, TokenType.DIVISION)
            next_fact = self.parse_fact()
            fact = MultDivMod(operator=op.value, operand1=fact, operand2=next_fact)
            next = self.peek()
        return fact

    def parse_addsub(self) -> Exp:
        term = self.parse_term()
        next = self.peek()
        while next.type == TokenType.ADDITION or next.type == TokenType.SUBTRACTION:
            op = self.check_type(TokenType.ADDITION, TokenType.SUBTRACTION)
            next_term = self.parse_term()
            term = AddSub(operator=op.value, operand1=term, operand2=next_term)
            next = self.peek()
        return term
    
    def parse_bit_shift(self) -> Exp:
        exp = self.parse_term()
        next = self.peek()
        while next.type == TokenType.BIT_SHIFT_LEFT or next.type == TokenType.BIT_SHIFT_RIGHT:
            op = self.check_type(TokenType.BIT_SHIFT_LEFT, TokenType.BIT_SHIFT_RIGHT)
            shift_amount = self.parse_term()
            exp = BitShift(operator=op.value, value=exp, shift=shift_amount)
            next = self.peek()
        return exp
    
    def parse_bit_and(self) -> Exp:
        exp = self.parse_bit_shift()
        next = self.peek()
        while next.type == TokenType.BIT_AND:
            self.pos += 1
            next_exp = self.parse_bit_shift()
            exp = BitAND(operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_bit_xor(self) -> Exp:
        exp = self.parse_bit_and()
        next = self.peek()
        while next.type == TokenType.BIT_XOR:
            self.pos += 1
            next_exp = self.parse_bit_and()
            exp = BitXOR(operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_bit_or(self) -> Exp:
        exp = self.parse_bit_xor()
        next = self.peek()
        while next.type == TokenType.BIT_OR:
            self.pos += 1
            next_exp = self.parse_bit_xor()
            exp = BitOR(operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp

    def parse_inequality(self) -> Exp:
        exp = self.parse_bit_or()
        next = self.peek()
        while (next.type == TokenType.LESS_THAN or next.type == TokenType.LESS_THAN_OR_EQUAL
        or next.type == TokenType.GREATER_THAN or next.type == TokenType.GREATER_THAN_OR_EQUAL):
            op = self.check_type(
                TokenType.LESS_THAN, TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN, TokenType.GREATER_THAN_OR_EQUAL
                )
            next_exp = self.parse_bit_or()
            exp = Inequality(operator=op.value, operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_equality(self) -> Exp:
        exp = self.parse_inequality()
        next = self.peek()
        while next.type == TokenType.EQUAL or next.type == TokenType.NOT_EQUAL:
            op = self.check_type(TokenType.EQUAL, TokenType.NOT_EQUAL)
            next_exp = self.parse_inequality()
            exp = Equality(operator=op.value, operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_and(self) -> Exp:
        exp = self.parse_equality()
        next = self.peek()
        while next.type == TokenType.AND:
            self.pos += 1
            next_exp = self.parse_equality()
            exp = AND(operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_or(self) -> Exp:
        exp = self.parse_and()
        next = self.peek()
        while next.type == TokenType.OR:
            self.pos += 1
            next_exp = self.parse_and()
            exp = OR(operand1=exp, operand2=next_exp)
            next = self.peek()
        return exp
    
    def parse_statement(self) -> Statement:
        self.check_type(TokenType.RETURN)
        exp = self.parse_or()
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