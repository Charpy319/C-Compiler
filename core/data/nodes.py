from dataclasses import dataclass
from typing import Union

# The dataclasses below represent the different types of nodes of the AST
@dataclass
class Parenthesis:
    exp: 'Exp'

@dataclass
class IntLiteral:
    value: int

@dataclass
class UnOp:
    operator: str
    operand: 'Exp'

@dataclass
class MultDivMod:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class AddSub:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class BitShift:
    operator: str
    value: 'Exp'
    shift: 'Exp'

@dataclass
class BitAND:
    operator = "&"
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class BitXOR:
    operator = "^"
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class BitOR:
    operator = "|"
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class Inequality:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class Equality:
    operator: str
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class AND:
    operator = "&&"
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class OR:
    operator = "||"
    operand1: 'Exp'
    operand2: 'Exp'

@dataclass
class Statement:
    expression: 'Exp'

@dataclass
class Function:
    name: str
    body: Statement

@dataclass
class Program:
    function: Function



# Union means that it can be of any of the types in the []
Exp = Union[
    OR, AND,
    Equality, Inequality,
    BitOR, BitXOR, BitAND, BitShift,
    AddSub, MultDivMod, 
    Parenthesis, UnOp, IntLiteral
    ]