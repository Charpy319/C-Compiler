from core.data.nodes import *

# Evaluates constant expressions
class Fold:
    def __init__(self, prog_node):
        self.prog_node = prog_node

    def start_fold(self):
        new_inits = []
        new_funcs = []
        for var in self.prog_node.init_vars:
            init = self.fold_glb_var(var)
            new_inits.append(var)
        for func in self.prog_node.funcs:
            function = self.fold_func(func)
            new_funcs.append(function)
        self.prog_node.init_vars = new_inits
        self.prog_node.funcs = new_funcs
        return self.prog_node

    def fold_func(self, func):
        func.body = self.fold_block(func.body)
        return func

    def fold_glb_var(self, var):
        new_exp = self.fold_exp(var.exp)
        var.exp = new_exp
        return var

    def fold_block(self, block):
        items = []
        for itm in block.block_items:
            itm = self.fold_statement(itm)
            if itm:
                items.append(itm)
        block.block_items = items
        return block

    def fold_statement(self, stm):
        if isinstance(stm, Declare):
             return self.fold_declare(stm)
        elif isinstance(stm, Return):
            return self.fold_return(stm)
        elif isinstance(stm, If):
            return self.fold_if(stm)
        elif isinstance(stm, For):
            return self.fold_for(stm)
        elif isinstance(stm, While) or isinstance(stm, DoWhile):
            return self.fold_while(stm)
        elif isinstance(stm, ExpStatement):
            return self.fold_exp_statement(stm)
        elif isinstance(stm, Block):
            return self.fold_block(stm)
        elif isinstance(stm, Continue) or isinstance(stm, Break):
            return stm

    def fold_declare(self, decl):
        new_exp = self.fold_exp(decl.exp)
        decl.exp = new_exp
        return decl

    def fold_return(self, ret):
        new_exp = self.fold_exp(ret.exp)
        ret.exp = new_exp
        return ret

    def fold_if(self, _if):
        new_cond = self.fold_exp(_if.condition)
        new_if = self.fold_statement(_if.if_statement)
        if _if.else_statement:
            new_else = self.fold_statement(_if.else_statement)
        if isinstance(new_cond, IntLiteral):
            if new_cond.value != 0:
                return new_if
            else:
                if _if.else_statement:
                    return new_else
                else:
                    return None
        else:
            _if.condition = new_cond
            _if.if_statement = new_if
            _if.else_statement = new_else if _if.else_statement else None
            return _if

    def fold_for(self, _for):
        new_init = self.fold_statement(_for.initial)
        new_cond = self.fold_exp_statement(_for.condition)
        new_post = self.fold_exp_statement(_for.post_exp)
        new_stm = self.fold_statement(_for.statement)
        _for.initial = new_init
        _for.condition = new_cond
        _for.post_exp = new_post
        _for.statement = new_stm
        return _for

    def fold_while(self, _while):
        new_cond = self.fold_exp(_while.condition)
        new_stm = self.fold_statement(_while.statement)
        _while.condition = new_cond
        _while.statement = new_stm
        return _while

    def fold_exp_statement(self, exp):
        if exp.exp:
            new_exp = self.fold_exp(exp.exp)
            exp.exp = new_exp
        return exp

    def fold_exp(self, exp):
        # Lowest level, can't fold more
        if (
            isinstance(exp, IntLiteral) or isinstance(exp, Var)
            or isinstance(exp, Increment) or isinstance(exp, Decrement)
            or isinstance(exp, FunctionCall)
        ):
            return exp
        # Fold the rest
        elif isinstance(exp, CommaExp):
            new_left = self.fold_exp(exp.lhs)
            new_right = self.fold_exp(exp.rhs)
            exp.lhs = new_left
            exp.rhs = new_right
            return exp

        elif isinstance(exp, Assign):
            new_exp = self.fold_exp(exp.exp)
            exp.exp = new_exp
            return exp

        elif isinstance(exp, Conditional):
            new_cond = self.fold_exp(exp.cond)
            new_if = self.fold_exp(exp.if_statement)
            new_else = self.fold_exp(exp.else_statement)
            if isinstance(new_cond, IntLiteral):
                if new_cond.value != 0:
                    return new_if
                else:
                    return new_else
            else:
                exp.condition = new_cond
                exp.if_statement = new_if
                exp.else_statement = new_else
                return exp

        elif isinstance(exp, OR):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if new_op1.value != 0 or new_op2.value != 0:
                    return IntLiteral(value=1, line=exp.line)
                else:
                    return IntLiteral(value=0, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, AND):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if new_op1.value != 0 and new_op2.value != 0:
                    return IntLiteral(value=1, line=exp.line)
                else:
                    return IntLiteral(value=0, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, Equality):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if exp.operator == TokenType.EQUAL:
                    if new_op1.value == new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
                elif exp.operator == TokenType.NOT_EQUAL:
                    if new_op1.value != new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, Inequality):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if exp.operator == TokenType.GREATER_THAN:
                    if new_op1.value > new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
                elif exp.operator == TokenType.GREATER_THAN_OR_EQUAL:
                    if new_op1.value >= new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
                elif exp.operator == TokenType.LESS_THAN:
                    if new_op1.value < new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
                elif exp.operator == TokenType.LESS_THAN_OR_EQUAL:
                    if new_op1.value <= new_op2.value:
                        return IntLiteral(value=1, line=exp.line)
                    else:
                        return IntLiteral(value=0, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, BitOR):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                value = new_op1.value | new_op2.value
                return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, BitXOR):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                value = new_op1.value ^ new_op2.value
                return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, BitAND):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                value = new_op1.value & new_op2.value
                return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, BitShift):
            new_val = self.fold_exp(exp.operand1)
            new_shift = self.fold_exp(exp.operand2)
            if isinstance(new_val, IntLiteral) and isinstance(new_shift, IntLiteral):
                if exp.operator == TokenType.BIT_SHIFT_LEFT:
                    value = new_val.value << new_shift.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.BIT_SHIFT_RIGHT:
                    value = new_val.value >> new_shift.value
                    return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_val
                exp.operand2 = new_shift
                return exp

        elif isinstance(exp, AddSub):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if exp.operator == TokenType.ADDITION:
                    value = new_op1.value + new_op2.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.SUBTRACTION:
                    value = new_op1.value - new_op2.value
                    return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, MultDivMod):
            new_op1 = self.fold_exp(exp.operand1)
            new_op2 = self.fold_exp(exp.operand2)
            if isinstance(new_op1, IntLiteral) and isinstance(new_op2, IntLiteral):
                if exp.operator == TokenType.MULTIPLICATION:
                    value = new_op1.value * new_op2.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.DIVISION:
                    value = new_op1.value // new_op2.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.MODULO:
                    value = new_op1.value % new_op2.value
                    return IntLiteral(value=value, line=exp.line)
            else:
                exp.operand1 = new_op1
                exp.operand2 = new_op2
                return exp

        elif isinstance(exp, UnOp):
            new_op = self.fold_exp(exp.operand)
            if isinstance(new_op, IntLiteral):
                if exp.operator == TokenType.BITCOMP:
                    value = ~new_op.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.SUBTRACTION:
                    value = -new_op.value
                    return IntLiteral(value=value, line=exp.line)
                elif exp.operator == TokenType.LOGICAL_NEGATION:
                    if new_op.value != 0:
                        return IntLiteral(value=0, line=exp.line)
                    else:
                        return IntLiteral(value=1, line=exp.line)
            else:
                exp.operand = new_op
                return exp

        elif isinstance(exp, Parenthesis):
            return self.fold_exp(exp.exp)