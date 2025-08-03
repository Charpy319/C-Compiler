# For inserting and retrieving entries to and from the symbol table. More will be explained in the documents
from core.data.token_types import TokenType
from typing import Optional
class SymbolEntry:
    def __init__(self, id: str, type: TokenType, initialised: bool, line: int):
        self.id = id
        self.type = type
        self.initialised = initialised
        self.line = line
        self.offset = None

class LabelEntry:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class SymbolTable:
    def __init__(self, fun_name: str = None, args: list[tuple] = None, return_type: TokenType = None):
        self.table = {}

    def insert(self, id: str, entry: SymbolEntry):
        self.table[id] = entry

    def get(self, id: str) -> SymbolEntry:
        return self.table[id]