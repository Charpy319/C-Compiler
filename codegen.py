"""
Now to generate code from this, I will need to traverse the AST and write into an assembly file
"""
from dataclasses import dataclass
from typing import Union
from parser import Program, Function, Statement, Exp, UnOp, IntLiteral, AddSub, MultDiv, Parenthesis
    
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
        
        elif isinstance(exp, AddSub):
            op = exp.operator
            if op == "+":
                return (
                    self.generate_exp(exp.operand1)
                    + "  pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"  
                    "  addq  %rcx,  %rax\n"
                )
            
            elif op == "-":
                return (
                    self.generate_exp(exp.operand2)
                    + "  pushq  %rax\n"
                    + self.generate_exp(exp.operand1)
                    + "  popq  %rcx\n"  
                    "  subq  %rcx,  %rax\n"
                )

        elif isinstance(exp, MultDiv):
            op = exp.operator
            if op == "*":
                return (
                   self.generate_exp(exp.operand1)  
                    + "  pushq  %rax\n"
                    + self.generate_exp(exp.operand2)  
                    + "  popq  %rcx\n"  
                    "  imulq  %rcx,  %rax\n"
                )
            elif op == "/":
                return (
                    self.generate_exp(exp.operand2)
                    + "  pushq  %rax\n"
                    + self.generate_exp(exp.operand1)
                    + "  popq  %rcx\n"
                    + "  cqo\n"
                    "  idivq  %rcx\n"
                )
        
        elif isinstance(exp, Parenthesis):
            return self.generate_exp(exp.exp)
        
        elif isinstance(exp, IntLiteral):
            return (
                f"  movq  ${~exp.value if self.bit_comp[0] == 1 else exp.value},  %rax\n"
                + (("  cmpq  $0,  %rax\n  movq  $0,  %rax\n  sete  %ral\n") if  self.bit_neg[0] == 1 else "")
                + (("  neg    %rax\n" if self.neg[0] == 1 else ""))
            )

    def generate_statement(self, stm: Statement) -> str:
        return (
            self.generate_exp(stm.expression)
            + "  ret"
        )
    
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
    