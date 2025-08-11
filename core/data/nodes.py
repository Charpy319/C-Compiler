from dataclasses import dataclass
from typing import Optional, Union
from core.util.symbol_table import SymbolTable
from core.data.token_types import TokenType

# The dataclasses below represent the different types of nodes of the AST

@dataclass
class Program:
    init_vars: list('GlobalVar')
    uninit_vars: list('GlobalVar')
    funcs: list('Function')

@dataclass
class GlobalVar:
    id: 'Var'
    type: TokenType
    exp: 'ExpStatement'
    line: int
    init: bool

@dataclass
class Function:
    name: str
    variables: list((TokenType, str))
    _return: TokenType
    prototype: bool
    body: Optional['Block'] = None

@dataclass
class Block:
    block_items: list('BlockItem')
    symboltable: SymbolTable

@dataclass
class Declare:
    id: 'Var'
    type: TokenType
    exp: 'ExpStatement'
    line: int

@dataclass
class Return:
    line: int
    exp: 'ExpStatement'

@dataclass
class If:
    condition: 'Exp'
    if_statement: 'Statement'
    else_statement: Optional['Statement'] = None

@dataclass
class For:
    initial: Union[Declare, 'ExpStatement']
    condition: 'Exp'
    post_exp: 'ExpStatement'
    statement: 'Statement'
    symboltable: SymbolTable

@dataclass
class While:
    condition: 'Exp'
    statement: 'Statement'

@dataclass
class DoWhile:
    statement: 'Statement'
    condition: 'Exp'

@dataclass
class Break:
    line: int

@dataclass
class Continue:
    line: int

@dataclass
class ExpStatement:
    line: int
    exp: Optional['Exp'] = None

@dataclass
class CommaExp:
    lhs: 'Exp'
    rhs: 'Exp'
    line: int

@dataclass
class Assign:
    id: 'Var'
    exp: 'Exp'
    line: int
    type: Optional[TokenType] = None

@dataclass 
class Conditional:
    condition: 'Exp'
    if_statement: 'Exp'
    else_statement: 'Exp'
    line: int

@dataclass
class OR:
    operator = TokenType.OR
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class AND:
    operator = TokenType.AND
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class Equality:
    operator: TokenType
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class Inequality:
    operator: TokenType
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class BitOR:
    operator = TokenType.BIT_OR
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class BitXOR:
    operator = TokenType.BIT_XOR
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class BitAND:
    operator = TokenType.BIT_AND
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class BitShift:
    operator: TokenType
    value: 'Exp'
    shift: 'Exp'
    line: int

@dataclass
class AddSub:
    operator: TokenType
    operand1: 'Exp'
    operand2: 'Exp'
    line: int


@dataclass
class MultDivMod:
    operator: TokenType
    operand1: 'Exp'
    operand2: 'Exp'
    line: int

@dataclass
class UnOp:
    operator: TokenType
    operand: 'Exp'
    line: int

@dataclass
class IntLiteral:
    value: int
    line: int

@dataclass
class Decrement:
    id: str
    prefix: bool
    line: int

@dataclass
class Increment:
    id: str
    prefix: bool
    line: int

@dataclass
class Var:
    id: str
    line: int
    type: Optional[TokenType] = None

@dataclass
class FunctionCall:
    name: str
    param: Optional[list('Exp')]
    line: int

@dataclass
class Parenthesis:
    exp: 'Exp'
    line: int



# Union means that it can be of any of the types in the []
Exp = Union[
    CommaExp, Assign,
    OR, AND,
    Equality, Inequality,
    BitOR, BitXOR, BitAND, BitShift,
    AddSub, MultDivMod, 
    UnOp, IntLiteral, Var, FunctionCall,
    Parenthesis
    ]

Statement = Union[Return, Declare, Exp, Block, ExpStatement, If, For, While, DoWhile, Break, Continue]

BlockItem = Union[Statement, Declare]

Top = Union[GlobalVar, Function]