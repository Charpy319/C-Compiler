import sys
import os
from .lexer import Lexer as lexer
from .parser import Parser as parser
from core.data.nodes import *

class PrettyPrinter:
    def __init__(self, ast: Program):
        self.ast = ast

    def print_exp(self, exp: Exp) -> str:
        if (
            isinstance(exp, OR) or isinstance(exp, AND)
            or isinstance(exp, BitOR) or isinstance(exp, BitXOR) or isinstance(exp, BitAND)
            or isinstance(exp, AddSub) or isinstance(exp, MultDivMod)
            or isinstance(exp, Inequality) or isinstance(exp, Equality)
         ):
            return f"{self.print_exp(exp.operand1)}{exp.operator}{self.print_exp(exp.operand2)}"
        
        elif isinstance(exp, BitShift):
            return f"{self.print_exp(exp.value)}{exp.operator}{self.print_exp(exp.shift)}"
        
        elif isinstance(exp, Parenthesis):
            return f"({self.print_exp(exp.exp)})"
            
        elif isinstance(exp, UnOp):
            return f"{exp.operator}{self.print_exp(exp.operand)}"
        
        elif isinstance(exp, Increment):
            if exp.prefix:
                return f"++{exp.id}"
            else:
                return f"{exp.id}++"
        
        elif isinstance(exp, Decrement):
            if exp.prefix:
                return f"--{exp.id}"
            else:
                return f"{exp.id}--"
            
        elif isinstance(exp, IntLiteral):
            return str(exp.value)
        
        elif isinstance(exp, Var):
            return exp.id

        elif isinstance(exp, CommaExp):
            return f"({self.print_exp(exp.lhs)}, {self.print_exp(exp.rhs)})"

        elif isinstance(exp, Assign):
            return f"{exp.id.id} = {self.print_exp(exp.exp)}"
    
    def print_statement(self, stm: Statement) -> str:
        if isinstance(stm, Declare):
            return (
            f"{stm.type} {stm.id.id}"
            + (f"={self.print_exp(stm.exp)}" if stm.exp != None else "")
        )

        elif isinstance(stm, Return):
            return f"RETURN {self.print_exp(stm.exp)}"

        elif isinstance(stm, ExpStatement):
            return self.print_exp(stm.exp)
    
    def print_function(self, func: Function) -> str:
            fun = f"FUN INT {func.name}:\n    params: ()\n    body:\n"
            for s in func.body: 
                fun += f"           {self.print_statement(s)}\n"
            return fun
    
    def print_program(self) -> str:
        return self.print_function(self.ast.function)
    
  
if len(sys.argv) < 2:
    print("Usage: python3 prettyprint.py <c_file>")
    sys.exit(1)

path = sys.argv[1]
if not os.path.exists(path):
    print(f"Error: file '{path}' could not be found")
    sys.exit(1)

with open(path, "r") as file:
    text = file.read()

tokens = lexer(text).tokenise()

ast = parser(tokens).parse_program()

pretty = PrettyPrinter(ast)
tree = pretty.print_program()

print(tree)
print(ast)