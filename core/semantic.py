# Takes in the AST from the parser, checking for types

from core.util.symbol_table import SymbolTable
from core.util.error import error
from core.data.token_types import TokenType
from core.data.nodes import*

class SemanticAnalyser:
    def __init__(self):
        self.table_stack = []
        self.operation_compatible = {
            TokenType.INT: {TokenType.INT, TokenType.CHAR, TokenType.FLOAT},
            TokenType.CHAR: {TokenType.CHAR, TokenType.INT, TokenType.FLOAT},
            TokenType.FLOAT: {TokenType.FLOAT, TokenType.INT, TokenType.CHAR},
        }

    def start(self, root: Program) -> Program:
        for func in root.functions:
            self.analyse_function(func)
        return root

    def analyse_function(self, fun: Function) -> None:
        self.table_stack.append(fun.symboltable)
        for stm in fun.body:
            self.analyse_statement(stm)
        return

    def analyse_statement(self, stm: Statement) -> None:
        if isinstance(stm, Return):
            self.analyse_return(stm)
        elif isinstance(stm, Declare):
            self.analyse_declare(stm)
        else:
            self.analyse_assign(stm.exp)
        return

    # TODO: Add in function calling compatibility
    def analyse_return(self, stm: Statement) -> None:
        symbol = self.table_stack.pop()
        expected = symbol.return_type
        if stm.exp:
            return_type = self.analyse_assign(stm.exp)
        if expected == TokenType.VOID and stm.exp:
            error.report(
                error_msg=f"Expected return type {expected.name}, got {return_type.name}",
                line=stm.line, type="TypeError"
                )
        
        self.table_stack.append(symbol)
        return

    def analyse_declare(self, stm: Statement) -> None:
        symbol = self.table_stack.pop()
        name = stm.id.id
        var = symbol.table.get(name)
        var_type = stm.type
        var.type = var_type
        exp_type = self.analyse_assign(stm.exp)
        if exp_type not in self.operation_compatible[var_type]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=stm.line, type="TypeError"
                )
        return 
    def analyse_assign(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Assign):
            return self.analyse_OR(exp)
        
        name = exp.id.id
        if name not in symbol.table:
            error.report(error_msg=f"{name} if not defined", line=exp.line, type="NameError")

        var = symbol.table.get(id)
        var_type = var.type
        exp_type = self.analyse_assign(exp.exp)
        if exp_type not in self.operation_compatible[var_type]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
                )
        return exp_type

    def analyse_OR(self, exp: Exp) -> TokenType:
        if not isinstance(exp, OR):
            return self.analyse_AND(exp)

        type1 = self.analyse_AND(exp.operand1)
        type2 = self.analyse_AND(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
                )
        return type1

    def analyse_AND(self, exp: Exp) -> TokenType:
        if not isinstance(exp, AND):
            return self.analyse_equality(exp)

        type1 = self.analyse_equality(exp.operand1)
        type2 = self.analyse_equality(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
                )
        return type1
    
    def analyse_equality(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_inequality(exp)

        type1 = self.analyse_inequality(exp.operand1)
        type2 = self.analyse_inequality(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_inequality(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_bit_or(exp)

        type1 = self.analyse_bit_or(exp.operand1)
        type2 = self.analyse_bit_or(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_bit_or(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_bit_xor(exp)

        type1 = self.analyse_bit_xor(exp.operand1)
        type2 = self.analyse_bit_xor(exp.operand2)
        if type1 == TokenType.FLOAT or type2 == TokenType.FLOAT:
            error.report(error_msg="Cannot perform operation on float", line=exp.line, type="TypeError")
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_bit_and(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_bit_shift(exp)

        type1 = self.analyse_bit_shift(exp.operand1)
        type2 = self.analyse_bit_shift(exp.operand2)
        if type1 == TokenType.FLOAT or type2 == TokenType.FLOAT:
            error.report(error_msg="Cannot perform operation on float", line=exp.line, type="TypeError")
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_bit_shift(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_addsub(exp)

        type1 = self.analyse_addsub(exp.operand1)
        type2 = self.analyse_addsub(exp.operand2)
        if type1 == TokenType.FLOAT or type2 == TokenType.FLOAT:
            error.report(error_msg="Cannot perform operation on float", line=exp.line, type="TypeError")
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_addsub(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_term(exp)

        type1 = self.analyse_term(exp.operand1)
        type2 = self.analyse_term(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1

    def analyse_term(self, exp: Exp) -> TokenType:
        if not isinstance(exp, Equality):
            return self.analyse_fact(exp)

        type1 = self.analyse_fact(exp.operand1)
        type2 = self.analyse_fact(exp.operand2)
        if type2 not in self.operation_compatible[type1]:
            error.report(
                error_msg=f"Cannot assign {exp_type.name} to variable '{id}' of type {var_type.name}",
                line=exp.line, type="TypeError"
            )
        return type1
    