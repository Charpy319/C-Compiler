"""
Now to generate code from this, I will need to traverse the AST and write into an assembly file
"""
from dataclasses import dataclass

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
    
class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root

    def generate_statement(self, stm: Statement) -> str:
        value = stm.expression.value
        return f"  movl   ${value}, %eax\n  ret"
    
    def generate_function(self, func: Function) -> str:
        return (
            f".globl _{func.name}\n_{func.name}:\n"
            + self.generate_statement(func.body)
        )
    
    def generate_program(self) -> str:
        return (
            ".section __TEXT,__text\n"
            + self.generate_function(self.root.function)
        )
    