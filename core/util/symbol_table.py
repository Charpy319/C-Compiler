# For inserting and retrieving entries to and from the symbol table. More will be explained in the documents
from core.data.token_types import TokenType
from typing import Optional
class SymbolEntry:
    
    def __init__(self, id: str, type: TokenType, initialised: bool):
        self.id = id
        self.type = type
        self.initialised = initialised
        self.offset = None

class SymbolTable:
    def __init__(self, fun_name: str = None, args: list[tuple] = None, return_type: TokenType = None):
        self.table = {}

    def insert(self, id: str, entry: SymbolEntry):
        self.table[id] = entry

    def get(self, id: str) -> Optional[SymbolEntry]:
        return self.table[id] if self.table[id] else None