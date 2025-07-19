import sys
from dataclasses import dataclass
from lexer import Lexer
from parser import Parser, Program, Function, Statement, Exp, UnOp, IntLiteral

class PrettyPrinter:
    def __init__(self, ast: Program):
        self.ast = ast

    def print_exp(self, exp: Exp) -> str:
        if isinstance(exp, UnOp):
            op = exp.operator
            if op == "~":
                return f"~{self.print_exp(exp.operand)}"
            elif op == "-":
                return f"-{self.print_exp(exp.operand)}"
            elif op == "!":
                return f"!{self.print_exp(exp.operand)}"
        elif isinstance(exp, IntLiteral):
            # Return the value directly for IntLiteral
            return str(exp.value)
        raise TypeError(f"Unknown expression type: {type(exp)}")
    
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