import sys
from dataclasses import dataclass
from lexer import Lexer
from parser import Parser

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

class PrettyPrinter:
    def __init__(self, ast: Program):
        self.ast = ast

    def print_exp(self, exp: Exp) -> str:
        return str(exp.value)
    
    def print_statement(self, stm: Statement) -> str:
        return (
            f"  return INT <{self.print_exp(stm.expression)}>"
        )
    
    def print_function(self, func: Function) -> str:
        return (
            f"FUN INT {func.name}:\n    params: ()\n    body: {self.print_statement(func.body)}"
        )
    
    def print_program(self) -> str:
        return self.print_function(self.ast.function)
    
if len(sys.argv) < 2:
    print("Usage: python3 prettyprint.py <c_file>")
    sys.exit(1)

with open(sys.argv[1], "r") as file:
    text = file.read()

l = Lexer(text)
tokens = l.tokenise()

p = Parser(tokens)
ast = p.parse_program()

pretty = PrettyPrinter(ast)
tree = pretty.print_program()

print(tree)