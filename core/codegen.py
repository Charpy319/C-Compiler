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
    TokenType.CHAR: 8,
}

class Memory:
    def __init__(self):
        self.memory = 0
        self.offset = 0
    
    def make_space(self, table: dict) -> int:
        mem = 0
        for sym in table:
            _type = table[sym].type
            mem += sizeof[_type]
        total_memory = 16 * math.ceil(mem / 16.0)   # Memory allocated in stack frame has to be a multiple of 16
        self.memory = total_memory
        return total_memory
    
    def assign_memory(self, id: str, table: dict, line: int) -> int:
        if self.memory == 0:
            error.report(error_msg="Error assigning memory, no available space", line=line, type="MemoryError")
            error.display("Code Generation")
        
        _type = table[id].type
        mem = sizeof[_type]
        self.memory -= mem
        self.offset -= mem
        entry = table[id]
        entry.offset = self.offset
        return self.offset
# TODO: write support for storing in different sizes
class CodeGenerator:
    def __init__(self, root: Program):
        self.root = root
        self.memory = Memory()
        self.table_stack = []

    def search_blocks(self, id: str, line: int = None):
        for i in range(-1, -len(self.table_stack) - 1, -1):
            symbol = self.table_stack[i]
            if id in symbol.table:
                if not line:    # For break, continue labels
                    return symbol.get(id)
                elif line >= symbol.table[id].line:
                    return (symbol.get(id), False)  # False for local
            if id in global_table and isinstance(global_table[id], SymbolEntry):
                return (global_table[id], True)   # True for global
        return None

    def padding(self, args) -> int:
        if len(args) % 2 == 1:
            return 8
        else:
            return 0
            
    def generate_program(self) -> str:
        assembly = ""
        if self.root.init_vars:
            assembly += "    .section __DATA,__data\n"
            for init_var in self.root.init_vars:
                assembly += self.generate_global_init(init_var)
            assembly += "\n\n"
        if self.root.uninit_vars:
            for uninit_var in self.root.uninit_vars:
                assembly += self.generate_global_uninit(uninit_var)
            assembly += "\n\n"
        if self.root.funcs:
            assembly += (
                "    .section __TEXT,__text\n"
                
            )
            for func in self.root.funcs:
                assembly += self.generate_function(func)
        return assembly
    # TODO: cant generate code as cannot calculate during run time so need calculate with python, check later
    def generate_global_init(self, gl_var: GlobalVar) -> str:
        variable = gl_var.id
        if not isinstance(gl_var.exp, IntLiteral):
            error.report(
                error_msg=f"Global variable '{variable.id}' can only contain constant expressions",
                line=variable.line, type="SyntaxError"
            ) 
            error.display("Code Generation")
        return (
            f"    .globl    _{variable.id}\n"
            "    .p2align    3\n"  # 2*2 = 4 for int, use 3 for simplicity right now
            f"_{variable.id}:\n"
            f"    .int    {gl_var.exp.value}\n"
        )
    
    def generate_global_uninit(self, gl_var: GlobalVar) -> str:
        variable = gl_var.id
        return f"    .zerofill __DATA,__bss,_{variable.id},8,3\n"

    def generate_function(self, func: Function) -> str:
        return  (
            f"    .globl    _{func.name}\n"
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
            stm = self.generate_statement(itm)
            if stm:
                assembly += stm
        self.table_stack.pop()
        return assembly
        
    def generate_statement(self, stm: Statement) -> str:
        if isinstance(stm, Return):
            return (
                self.generate_exp(stm.exp) +
                "    movq    %rbp, %rsp\n"
                "    popq    %rbp\n"
                "    ret\n\n"
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
            assembly = ""
            if stm.symboltable:
                symbol = stm.symboltable
                self.table_stack.append(symbol)
                memory = self.memory.make_space(symbol.table)
                assembly += f"    subq    ${memory}, %rsp\n"
            else:
                symbol = self.table_stack[-1]
            assembly += (self.generate_statement(stm.initial) if stm.initial.exp else "")
            start = LabelGen.generate('start')
            end = LabelGen.generate('end')
            cont = LabelGen.generate('cont')
            symbol.insert(id="_continue", entry=LabelEntry(id="_continue", name=cont))
            symbol.insert(id="_break", entry=LabelEntry(id="_break", name=end))
            condition = self.generate_statement(stm.condition)
            if not condition:
                condition = ""
            post_exp = self.generate_statement(stm.post_exp)
            if not post_exp:
                post_exp = ""
            statement = self.generate_statement(stm.statement)
            if not statement:
                statement = ""
            symbol.pop("_continue")
            symbol.pop("_break")
            if isinstance(stm.initial, Declare):
                self.table_stack.pop()
            assembly += (
                f"_{start}:\n" +
                condition +
                "    cmpq    $0, %rax\n"
                f"    je    _{end}\n" +
                statement +
                f"_{cont}:\n" +
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
            condition = self.generate_exp(stm.condition)
            if not condition:
                condition = ""
            statement = self.generate_statement(stm.statement)
            if not statement:
                statement = ""
            symbol.pop("_continue")
            symbol.pop("_break")
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
            condition = self.generate_exp(stm.condition)
            if not condition:
                condition = ""
            statement = self.generate_statement(stm.statement)
            if not statement:
                statement = ""
            symbol.pop("_continue")
            symbol.pop("_break")
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
            br = self.search_blocks(id="_break")
            if not br:
                error.report(error_msg="Break can only be used in loops", line=stm.line, type="SyntaxError")
                error.display("Code Generation")
            return f"    jmp    _{br.name}\n"

        elif isinstance(stm, Continue):
            cn = self.search_blocks(id="_continue")
            if not cn:
                error.report(error_msg="Continue can only be used in loops", line=stm.line, type="SyntaxError")
                error.display("Code Generaton")
            return f"    jmp _{cn.name}\n"
            
        elif isinstance(stm, ExpStatement):
            if not stm.exp:
                return None
            else:
                return self.generate_exp(stm.exp)
                
        # Declare kept here as for sake of compactness, although technically not a statement
        elif isinstance(stm, Declare):
            symbol = self.table_stack[-1]
            variable = stm.id
            offset = self.memory.assign_memory(variable.id, symbol.table, stm.line)
            if stm.exp:
                return (
                    self.generate_exp(stm.exp) +
                    f"    movq    %rax, {offset}(%rbp)\n"
                )
            else:
                return ""
        elif isinstance(stm, Block):
            return self.generate_block(stm)
        else:
            return self.generate_exp(stm.exp)

    def generate_exp(self, exp: Exp) -> str:

        if isinstance(exp, CommaExp):
            return f"{self.generate_exp(exp.lhs)}{self.generate_exp(exp.rhs)}"
        
        elif isinstance(exp, Assign):
            var, _global = self.search_blocks(exp.id.id, exp.line)
            assembly = self.generate_exp(exp.exp)
            if _global:
                assembly += f"    movq    %rax, _{var.id}(%rip)\n"
            else:
                assembly += f"    movq    %rax, {var.offset}(%rbp)\n"
            return assembly
        
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
                f"    je    _{clause}\n"
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
            var, _global = self.search_blocks(exp.id, exp.line)
            if exp.prefix == True:
                if _global:
                    return (
                        f"    movq    _{var.id}(%rip), %rax\n"
                        "    dec    %rax\n"
                        f"    movq    %rax, _{var.id}(%rip)\n"
                    )
                else:
                    return (
                        f"    movq    {var.offset}(%rbp), %rax\n"
                        "    dec    %rax\n"
                        f"    movq    %rax, {var.offset}(%rbp)\n"
                    )
            elif exp.prefix == False:   #Postfix increment
                if _global:
                    return (
                        f"    movq    _{var.id}(%rip), %rax\n"
                        "    movq    %rax, %rcx\n"
                        "    dec    %rcx\n"
                        f"    movq    %rcx, _{var.id}(%rip)\n"
                    )
                else:
                    return (
                    f"    movq    {var.offset}(%rbp), %rax\n"
                    "    movq    %rax, %rcx\n"
                    "    dec    %rcx\n"
                    f"    movq    %rcx, {var.offset}(%rbp)\n"
                    )

        elif isinstance(exp, Increment):
            var, _global = self.search_blocks(exp.id, exp.line)
            if exp.prefix == True:  #Prefix increment
                if _global:
                    return (
                        f"    movq    _{var.id}(%rip), %rax\n"
                        "    inc    %rax\n"
                        f"    movq    %rax, _{var.id}(%rip)\n"
                    )
                else:
                    return (
                        f"    movq    {var.offset}(%rbp), %rax\n"
                        "    inc    %rax\n"
                        f"    movq    %rax, {var.offset}(%rbp)\n"
                    )
            elif exp.prefix == False:   #Postfix increment
                if _global:
                    return (
                        f"    movq    _{var.id}(%rip), %rax\n"
                        "    movq    %rax, %rcx\n"
                        "    inc    %rcx\n"
                        f"    movq    %rcx, _{var.id}(%rip)\n"
                    )
                else:
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
            var, _global = self.search_blocks(exp.id, exp.line)
            if _global:
                return f"    movq    _{var.id}(%rip), %rax\n"
            else:
                return f"    movq    {var.offset}(%rbp), %rax\n"

        elif isinstance(exp, Parenthesis):
            return self.generate_exp(exp.exp)
        
        elif isinstance(exp, FunctionCall):
            assembly = ""
            params = exp.param
            padding = self.padding(params)
            if padding:
                assembly += f"    subq    ${padding}, %rsp\n"
            for i in range(len(params)):
                assembly += (
                    self.generate_exp(params[i]) +
                    "    pushq    %rax\n"
                )
            assembly += f"    call    _{exp.name}\n"
            if params:
                cleanup = 8 * len(params)
                assembly += (
                    f"    addq    ${cleanup}, %rsp\n" +
                    (f"    addq    ${padding}, %rsp\n" if padding else "")
                    )
            return assembly

        else:
            error.report(error_msg=f"Incorrect use of {exp}", line=exp.line, type="SyntaxError")