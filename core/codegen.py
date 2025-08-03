"""The code generator generates the assembly from the AST, to see more on what each assembly line does, go to the documents"""
from core.data.token_types import*
from core.data.nodes import *
from core.util.symbol_table import *
from collections import defaultdict
import math
from core.util.error import error

# Generates unique labels for jumps
class LabelGen:
    count = defaultdict(int)

    @classmethod
    def generate(cls, name):
        cls.count[name] += 1
        return f"{name}{cls.count[name]}"

sizeof = {
    TokenType.INT: 8,
    TokenType.FLOAT: 8,
    TokenType.CHAR: 1,
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
    
    def assign_memory(self, id: str, table: dict, line: int) -> int:
        if self.memory == 0:
            error.report(error_msg="Error assigning memory, no available space", line=line, type="MemoryError")
            error.display("Code Generation")
        
        self.memory -= 8
        self.offset -= 8
        entry = table[id]
        entry.offset = self.offset
        return self.offset

class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root
        self.memory = Memory()
        self.table_stack = []

    def search_blocks(self, id: str, line: int = None) -> int:
        for i in range(-1, -len(self.table_stack) - 1, -1):
            symbol = self.table_stack[i]
            if id in symbol.table:
                if line and line >= symbol.table[id].line:
                    return symbol.get(id)
            

    def generate_program(self) -> str:
        assembly = ".section __TEXT,__text\n"
        for func in self.root.functions:
            assembly += self.generate_function(func)
        return assembly

    def generate_function(self, func: Function) -> str:
        return  (
            f".globl   _{func.name}\n"
            f"_{func.name}:\n" +
            "    pushq    %rbp\n"
            "    movq    %rsp, %rbp\n" +
            self.generate_block(func.body)
        )

    def generate_block(self, blk: Block) -> str:
        symbol = blk.symboltable
        self.table_stack.append(symbol)
        memory = self.memory.make_space(symbol.table)
        assembly = ""
        if memory != 0:
            assembly += f"    subq    ${memory}, %rsp\n"
        for itm in blk.block_items:
            assembly += self.generate_statement(itm)
        self.table_stack.pop()
        return assembly
        
    def generate_statement(self, stm: Statement) -> str:

        if isinstance(stm, Return):
            return (
                self.generate_exp(stm.exp) +
                "    movq    %rbp, %rsp\n"
                "    popq    %rbp\n"
                "    ret\n"
            )
            
        elif isinstance(stm, If):
            end = LabelGen.generate("end")
            if stm.else_statement:
                el = LabelGen.generate("el")
                return (
                    self.generate_exp(stm.condition) +
                    "    cmpq    $0, %rax\n"
                    f"    je    _{el}\n" +
                    self.generate_statement(stm.if_statement) +
                    f"    jmp    _{end}\n"
                    f"_{el}:\n" +
                    self.generate_statement(stm.else_statement) +
                    f"_{end}:\n"
                )
            else:
                return (
                    self.generate_exp(stm.condition) +
                    "    cmpq    $0, %rax\n"
                    f"    je    _{end}\n" +
                    self.generate_statement(stm.if_statement) +
                    f"_{end}:\n"
                )

        elif isinstance(stm, For):
            assembly = (self.generate_statement(stm.initial) if stm.initial.exp else "")  # Not generate_exp as could be of type ExpStatement
            start = LabelGen.generate('start')
            end = LabelGen.generate('end')
            cont = LabelGen.generate('cont')
            if stm.symboltable:
                symbol = stm.symboltable
                self.table_stack.append(symbol)
            else:
                symbol = self.table_stack[-1]
            symbol.insert(id="_continue", entry=LabelEntry(id="_continue", name=cont))
            symbol.insert(id="_break", entry=LabelEntry(id="_break", name=end))
            condition = self.generate_statement(stm.condition)
            post_exp = self.generate_statement(stm.post_exp)
            statement = self.generate_block(stm.statement)
            assembly += (
                f"_{start}:\n" +
                condition +
                "    cmpq    $0, %rax\n"
                f"    je    _{end}\n" +
                statement +
                f"_{cont}:\n" +
                # TODO: post_exp is none so cant concactenate so need to write condition, same for others
                (post_exp if stm.post_exp.exp else "") +
                f"    jmp    _{start}\n"
                f"_{end}:\n"
            )
            return assembly

        elif isinstance(stm, While):
            start = LabelGen.generate('start')
            end = LabelGen.generate('end')
            symbol = self.table_stack[-1]
            symbol.insert(id="_continue", entry=LabelEntry(id="_continue", name=start))
            symbol.insert(id="_break", entry=LabelEntry(id="_break", name=end))
            condition = self.generate_statement(stm.condition)
            statement = self.generate_block(stm.statement)
            return (
                f"_{start}:" +
                condition +
                "    cmpq    $0, %rax\n"
                f"    je    _{end}\n" +
                statement +
                f"    jmp    _{start}\n"
                f"_{end}:\n"
            )

        elif isinstance(stm, DoWhile):
            start = LabelGen.generate('start')
            end = LabelGen.generate('end')
            symbol = self.table_stack[-1]
            symbol.insert(id="_continue", entry=LabelEntry(id="_continue", name=start))
            symbol.insert(id="_break", entry=LabelEntry(id="_break", name=end))
            condition = self.generate_statement(stm.condition)
            statement = self.generate_block(stm.statement)
            return (
                f"_{start}:" +
                statement +
                condition +
                "    cmpq    $0, %rax\n"
                f"    je    _{end}\n"
                f"    jmp    _{start}\n"
                f"_{end}:\n"
            )
        
        elif isinstance(stm, Break):
            br = self.search_blocks("_break")
            return f"    jmp    _{br.name}\n"

        elif isinstance(stm, Continue):
            cn = self.search_blocks("_continue")
            return f"    jmp _{cn.name}\n"
            
        elif isinstance(stm, ExpStatement):
            if not stm.exp:
                return
            else:
                return self.generate_exp(stm.exp)
                
        # Declare kept here as for sake of compactness, although technically not a statement
        elif isinstance(stm, Declare):
            symbol = self.table_stack[-1]
            variable = stm.id
            offset = self.memory.assign_memory(variable.id, symbol.table, stm.line)
            return (
                (self.generate_exp(stm.exp) if stm.exp else "    movq    $0, %rax\n") +
                f"    movq    %rax, {offset}(%rbp)\n"
            )
        elif isinstance(stm, Block):
            return self.generate_block(stm)
        else:
            return self.generate_exp(stm.exp)

    def generate_exp(self, exp: Exp) -> str:

        if isinstance(exp, CommaExp):
            return f"{self.generate_exp(exp.lhs)}{self.generate_exp(exp.rhs)}"
        
        elif isinstance(exp, Assign):
            var = self.search_blocks(exp.id.id, exp.line)
            return (
                self.generate_exp(exp.exp) +
                f"    movq    %rax, {var.offset}(%rbp)\n"
            )
        
        elif isinstance(exp, Conditional):
            end = LabelGen.generate("end")
            el = LabelGen.generate("el")
            return (
                self.generate_exp(exp.condition) +
                "    cmpq    $0, %rax\n"
                f"    je    _{el}\n" +
                self.generate_exp(exp.if_statement) +
                f"    jmp    _{end}\n"
                f"_{el}:\n" +
                self.generate_exp(exp.else_statement) +
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
        
        elif isinstance(exp, Equality) or isinstance(exp, Inequality):
            op = exp.operator
            if op == TokenType.EQUAL:
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
            elif op == TokenType.NOT_EQUAL:
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
            
            elif op == TokenType.GREATER_THAN:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setg    %al\n"
                    "    movzx    %al, %rax\n"
                )

            elif op == TokenType.GREATER_THAN_OR_EQUAL:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setge    %al\n"
                    "    movzx    %al, %rax\n"
                )

            elif op == TokenType.LESS_THAN:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setl    %al\n"
                    "    movzx    %al, %rax\n"
                )

            elif op == TokenType.LESS_THAN_OR_EQUAL:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cmpq    %rcx, %rax\n"
                    "    movq    $0, %rax\n"
                    "    setle    %al\n"
                    "    movzx    %al, %rax\n"
                )
        
        elif isinstance(exp, BitOR):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %rcx\n"
                "    orq    %rcx, %rax\n"
            )

        elif isinstance(exp, BitXOR):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %rcx\n"
                "    xorq    %rcx, %rax\n"
            )

        elif isinstance(exp, BitAND):
            return (
                self.generate_exp(exp.operand1) +
                "    pushq    %rax\n" +
                self.generate_exp(exp.operand2) +
                "    popq    %%rcs\n"
                "    andq    %rcx, %rax\n"
            )

        elif isinstance(exp, BitShift):
            op = exp.operator
            if op == TokenType.BIT_SHIFT_LEFT:
                return (
                    self.generate_exp(exp.shift) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.value) +
                    "    popq    %rcx\n"
                    "    salq    %cl, %rax\n"
                )
               
            elif op == TokenType.BIT_SHIFT_RIGHT:
                return (
                    self.generate_exp(exp.shift) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.value) +
                    "    popq    %rcx\n"
                    "    sarq    %cl, %rax\n"
                )

        elif isinstance(exp, AddSub):
            op = exp.operator
            if op == TokenType.ADDITION:
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    addq    %rcx, %rax\n"
                )
            elif op == TokenType.SUBTRACTION:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    subq    %rcx, %rax\n"
                )
        
        elif isinstance(exp, MultDivMod):
            op = exp.operator
            if op == TokenType.MULTIPLICATION:
                return (
                    self.generate_exp(exp.operand1) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand2) +
                    "    popq    %rcx\n"
                    "    imulq    %rcx, %rax\n"
                )
            elif op == TokenType.DIVISION:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cqo\n"
                    "    idivq    %rcx\n"
                )
            elif op == TokenType.MODULO:
                return (
                    self.generate_exp(exp.operand2) +
                    "    pushq    %rax\n" +
                    self.generate_exp(exp.operand1) +
                    "    popq    %rcx\n"
                    "    cqo\n"
                    "    idivq    %rcx\n"
                    "    movq    %rdx, %rax\n"
                )

        elif isinstance(exp, Decrement):
            var = self.search_blocks(exp.id, exp.line)
            if exp.prefix == True:
                return (
                    f"    movq    {var.offset}(%rbp), %rax\n"
                    "    dec    %rax\n"
                    f"    movq    %rax, {var.offser}(%rbp)\n"
                )
            elif exp.prefix == False:
                return (
                    f"    movq    {var.offset}(%rbp), %rax\n"
                    "    movq    %rax, %rcx\n"
                    "    dec    %rcx\n"
                    f"    movq    %rcx, {var.offset}(%rbp)\n"
                )

        elif isinstance(exp, Increment):
            var = self.search_blocks(exp.id, exp.line)
            if exp.prefix == True:  #Prefix increment
                return (
                    f"    movq    {var.offset}(%rbp), %rax\n"
                    "    inc    %rax\n"
                    f"    movq    %rax, {var.offset}(%rbp)\n"
                )
            elif exp.prefix == False:   #Postfix increment
                return (
                    f"    movq    {var.offset}(%rbp), %rax\n"
                    "    movq    %rax, %rcx\n"
                    "    inc    %rcx\n"
                    f"    movq    %rcx, {var.offset}(%rbp)\n"
                )

        elif isinstance(exp, UnOp):
            op = exp.operator
            if op == TokenType.BIT_COMP:
                return self.generate_exp(exp.operand) + "    not    %rax\n"
            elif op == TokenType.SUBTRACTION:
                return self.generate_exp(exp.operand) + "    neg    %rax\n"
            elif op == TokenType.LOGICAL_NEGATION:
                return (
                    self.generate_exp(exp.operand) +
                    "    cmpq   $0, %rax\n"
                    "    movq   $0, %rax\n"
                    "    sete   %al\n"
                    "    movzx    %al, %rax\n"
                )

        elif isinstance(exp, IntLiteral):
            return f"    movq    ${exp.value}, %rax\n"


        elif isinstance(exp, Var):
            var = self.search_blocks(exp.id, exp.line)
            return f"    movq    {var.offset}(%rbp), %rax\n"

        elif isinstance(exp, Parenthesis):
            return self.generate_exp(exp.exp)
        
        else:
            error.report(error_msg=f"Incorrect use of {exp}", line=exp.line, type="Syntax")