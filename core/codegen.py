"""
Now to generate code from this, I will need to traverse the AST and write into an assembly file
"""
from core.data.nodes import *
from core.util.label import LabelGen
    
class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root

    def generate_exp(self, exp: Exp) -> str:
        if isinstance(exp, UnOp):
            op = exp.operator
            if op == "~":
                return (
                    self.generate_exp(exp.operand) 
                    + "  not %rax\n"
                )
            elif op == "-":
                return (
                    self.generate_exp(exp.operand)
                    + "  neg %rax\n"
                )
            elif op == "!":
                return (
                    self.generate_exp(exp.operand)
                    + "  cmpq  $0,  %rax\n"
                    "  movq  $0,  %rax\n"
                    "  sete %al\n"
                    "  movzx  %al,  %rax\n"
                )
        
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
            return f"  movq  ${exp.value},  %rax\n"
        
        elif isinstance(exp, Equality) or isinstance(exp, Inequality):
            op = exp.operator
            if op == "==":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  sete  %al\n"
                    "  movzx  %al,  %rax\n"
                )
            elif op == "!=":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  setne  %al\n"
                    "  movzx  %al,  %rax\n"
                )
            elif op == ">=":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  setge  %al\n"
                    "  movzx  %al,  %rax\n"
                )
            elif op == ">":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  setg  %al\n"
                    "  movzx  %al,  %rax\n"
                )
            elif op == "<=":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  setle  %al\n"
                    "  movzx  %al,  %rax\n"
                )
            elif op == "<":
                return (
                    self.generate_exp(exp.operand1)
                    + " pushq  %rax\n"
                    + self.generate_exp(exp.operand2)
                    + "  popq  %rcx\n"
                    "  cmpq  %rax,  %rcx\n"
                    "  movq  $0,  %rax\n"
                    "  setl  %al\n"
                    "  movzx  %al,  %rax\n"
                )
        
        elif isinstance(exp, OR):
            clause = LabelGen.generate("clause")
            end = LabelGen.generate("end")
            return (
                self.generate_exp(exp.operand1)
                + "  cmpq  $0,  %rax\n"
                f"  je  _{clause}\n"
                "  movq  $1,  %rax\n"
                "  movzx  %al,  %rax\n"
                f"  jmp  _{end}\n"
                f"_{clause}:\n"
                + self.generate_exp(exp.operand2)
                + "  cmpq  $0,  %rax\n"
                "  movq  $0,  %rax\n"
                "  setne  %al\n"
                "  movzx  %al,  %rax\n"
                f"_{end}:\n"
            )
        
        elif isinstance(exp, AND):
            clause = LabelGen.generate("clause")
            end = LabelGen.generate("end")
            return (
                self.generate_exp(exp.operand1)
                + "  cmpq  $0,  %rax\n"
                f"  jne  _{clause}\n"
                f"  je  _{end}\n"
                f"_{clause}:\n"
                + self.generate_exp(exp.operand2)
                + "  cmpq  $0,  %rax\n"
                "  movq  $0,  %rax\n"
                "  setne  %al\n"
                "  movzx  %al,  %rax\n"
                f"_{end}:\n"
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
    