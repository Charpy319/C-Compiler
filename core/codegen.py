"""The code generator generates the assembly from the AST, to see more on what each assembly line does, go to the documents"""

from core.data.nodes import *
from core.util.symbol_table import symbol, SymbolEntry
from collections import defaultdict
import math

# Generates unique labels for jumps
class LabelGen:
    count = defaultdict(int)

    @classmethod
    def generate(cls, name):
        cls.count[name] += 1
        return f"{name}{cls.count[name]}"

sizeof = {
    "int": 4,
    "float": 8,
    "char": 1,
    "bool": 1
}

class Memory:
    def __init__(self):
        self.memory = 0
        self.offset = 0
    
    def make_space(self, table: dict) -> int:
        mem = 0
        for sym in table:
            type = table[sym].type
            mem += sizeof[type]
        total_memory = 16 * math.ceil(mem / 16.0)   # Memory allocated in stack frame has to be a multiple of 16
        self.memory = total_memory
        return total_memory
    
    def assign_memory(self, id: str) -> int:
        if self.memory == 0:
            raise MemoryError("No space available yet")
        
        self.memory -= 8
        self.offset -= 8
        entry = symbol.get(id)
        entry.offset = self.offset
        return self.offset

class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root
        self.memory = Memory()
        self.total_memory = self.memory.make_space(symbol.table)

    # The order of the conditionals correspond to the pecedence of each node
    def generate_exp(self, exp: Exp) -> str:
        if isinstance(exp, Parenthesis):
            return self.generate_exp(exp.exp)

        elif isinstance(exp, IntLiteral):
            return f"    movq    ${exp.value}, %rax\n"

        elif isinstance(exp, UnOp):
            op = exp.operator
            if op == "~":
                return self.generate_exp(exp.operand) + "    not    %rax\n"
            elif op == "-":
                return self.generate_exp(exp.operand) + "    neg    %rax\n"
            elif op == "!":
                return (
                    self.generate_exp(exp.operand) +
                    "    cmpq   $0, %rax\n"
                    "    movq   $0, %rax\n"
                    "    sete   %al\n"
                    "    movzx    %al, %rax\n"
                )
        
        elif isinstance(exp, Increment):
            offset = symbol.get(exp.id).offset
            if exp.prefix == True:  #Prefix increment
                return (
                    f"    movq    {offset}(%rbp), %rax\n"
                    "    inc    %rax\n"
                    f"    movq    %rax, {offset}(%rbp)\n"
                )
            elif exp.prefix == False:   #Postfix increment
                return (
                    f"    movq    {offset}(%rbp), %rax\n"
                    "    movq    %rax, %rcx\n"
                    "    inc    %rcx\n"
                    f"    movq    %rcx, {offset}(%rbp)\n"
                )

        elif isinstance(exp, Decrement):
            offset = symbol.get(exp.id).offset
            if exp.prefix == True:
                return (
                    f"    movq    {offset}(%rbp), %rax\n"
                    "    dec    %rax\n"
                    f"    movq    %rax, {offset}(%rbp)\n"
                )
            elif exp.prefix == False:
                return (
                    f"    movq    {offset}(%rbp), %rax\n"
                    "    movq    %rax, %rcx\n"
                    "    dec    %rcx\n"
                    f"    movq    %rcx, {offset}(%rbp)\n"
                )

        
        elif isinstance(exp, Var):
            offset = symbol.get(exp.id).offset
            return f"    movq    {offset}(%rbp), %rax\n"

        elif isinstance(exp, MultDivMod):
            op = exp.operator
            if op == "*":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    imulq    %rcx, %rax\n"
                )
            elif op == "/":
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cqo\n"
                    "    idivq    %rcx\n"
                )
            elif op == "%":
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cqo\n"
                    "    idivq    %rcx\n"
                    "    movq    %rdx, %rax\n"
                )

        elif isinstance(exp, AddSub):
            op = exp.operator
            if op == "+":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    addq    %rcx, %rax\n"
                )
            elif op == "-":
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    subq    %rcx, %rax\n"
                )

        elif isinstance(exp, BitShift):
            op = exp.operator
            if op == "<<":
                return (
                    self.generate_exp(exp.shift) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.value) +
                    "    popq    %rcx\n"
                    "    salq    %cl, %rax\n"
                )
            elif op == ">>":
                return (
                    self.generate_exp(exp.shift) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.value) +
                    "    popq    %rcx\n"
                    "    sarq    %cl, %rax\n"
                )

        elif isinstance(exp, BitAND):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %rcx\n"
                "    andq    %rcx, %rax\n"
            )

        elif isinstance(exp, BitXOR):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %rcx\n"
                "    xorq    %rcx, %rax\n"
            )

        elif isinstance(exp, BitOR):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %rcx\n"
                "    orq    %rcx, %rax\n"
            )

        elif isinstance(exp, Equality) or isinstance(exp, Inequality):
            op = exp.operator
            if op == "==":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    sete    %al\n"
                    "    movzx    %al, %rax\n"
                )
            elif op == "!=":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setne    %al\n"
                    "    movzx    %al, %rax\n"
                )
            elif op == ">=":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setge    %al\n"
                    "    movzx    %al, %rax\n"
                )
            elif op == ">":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setg    %al\n"
                    "    movzx    %al, %rax\n"
                )
            elif op == "<=":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setle    %al\n"
                    "    movzx    %al, %rax\n"
                )
            elif op == "<":
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setl    %al\n"
                    "    movzx    %al, %rax\n"
                )

        elif isinstance(exp, AND):
            clause = LabelGen.generate("clause")
            end = LabelGen.generate("end")
            return (
                self.generate_exp(exp.operand1) +
                "    cmpq    $0, %rax\n"
                f"    je    _{end}\n"
                f"_{clause}:\n" +
                self.generate_exp(exp.operand2) +
                "    cmpq    $0, %rax\n"
                "    movq   $0, %rax\n"
                "    setne    %al\n"
                "    movzx    %al, %rax\n"
                f"_{end}:\n"
            )

        elif isinstance(exp, OR):
            clause = LabelGen.generate("clause")
            end = LabelGen.generate("end")
            return (
                self.generate_exp(exp.operand1) +
                "    cmpq    $0, %rax\n"
                f"    jne    _{end}\n"
                "    movq    $1, %rax\n"
                "    movzx    %al, %rax\n"
                f"    jmp    _{end}\n"
                f"_{clause}:\n" +
                self.generate_exp(exp.operand2) +
                "    cmpq    $0, %rax\n"
                "    movq    $0, %rax\n"
                "    setne    %al\n"
                "    movzx    %al, %rax\n"
                f"_{end}:\n"
            )
        
        elif isinstance(exp, Assign):
            variable = exp.id
            offset = symbol.get(variable.id).offset
            return (
                self.generate_exp(exp.exp) +
                f"    movq    %rax, {offset}(%rbp)\n"
            )
        
        elif isinstance(exp, CommaExp):
            return f"{self.generate_exp(exp.lhs)}{self.generate_exp(exp.rhs)}"

    def generate_statement(self, stm: Statement) -> str:

        if isinstance(stm, Return):
            return (
                self.generate_exp(stm.exp) +
                "    movq    %rbp, %rsp\n"
                "    popq    %rbp\n"
                "    ret\n"
            )

        elif isinstance(stm, Declare):
            variable = stm.id
            offset = self.memory.assign_memory(variable.id)
            return (
                (self.generate_exp(stm.exp) if stm.exp else "    movq    $0, %rax\n") +
                f"    movq    %rax, {offset}(%rbp)\n"
            )

        else:
            return self.generate_exp(stm.exp)

    def generate_function(self, func: Function) -> str:
        assembly = (
            f".globl   _{func.name}\n"
            f"_{func.name}:\n" +
            "    pushq    %rbp\n"
            "    movq    %rsp, %rbp\n"
        )
        if self.total_memory != 0:
            assembly += f"    subq    ${self.total_memory}, %rsp\n"
        for stm in func.body:
            assembly += self.generate_statement(stm)
        last_statement = func.body[-1]
        if not isinstance(last_statement, Return):  # If there is no return from function, return 0
            assembly += (
                "    movq    $0, %rax\n"
                "    movq    %rbp, %rsp\n"
                "    popq    %rbp\n"
                "    ret\n"
            )
        
        return assembly

    def generate_program(self) -> str:
        return (
            ".section __TEXT,__text\n" +
            self.generate_function(self.root.function)
        )