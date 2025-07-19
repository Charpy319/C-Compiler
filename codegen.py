"""
Now to generate code from this, I will need to traverse the AST and write into an assembly file
"""
from dataclasses import dataclass
from typing import Union
from parser import Program, Function, Statement, Exp, UnOp, IntLiteral
    
class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root
        self.neg = [0]
        self.bit_comp = [0]
        self.bit_neg = [0]

    def generate_exp(self, exp: Exp) -> str:
        if isinstance(exp, UnOp):
            op = exp.operator
            if op == "~":
                self.bit_comp[0] = 1 - self.bit_comp[0]
            elif op == "-":
                self.neg[0] = 1 - self.neg[0]
            elif op == "!":
                self.bit_neg[0] = 1 - self.bit_neg[0]
            
            return self.generate_exp(exp.operand)

        elif isinstance(exp, IntLiteral):
            return (f"  movl   ${~exp.value if self.bit_comp[0] == 1 else exp.value}, %eax\n  "
                    + (("cmpl    $0, %eax\n  movl    $0, %eax\n  sete    %al\n  ") if  self.bit_neg[0] == 1 else "")
                    + (("neg    %eax\n  " if self.neg[0] == 1 else ""))
                    + "ret"
                    )

    def generate_statement(self, stm: Statement) -> str:
        return self.generate_exp(stm.expression)
        
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
    