# For inserting and retrieving entries to and from the symbol table. More will be explained in the documents
class SymbolEntry:
    
    def __init__(self, id: str, type: str, initialised: bool):
        self.id = id
        self.type = type
        self.initialised = initialised
        self.offset = None

class SymbolTable:
    def __init__(self):
        self.table = {}

    def insert(self, id, entry):
        self.table[id] = entry

    def get(self, id):
        return self.table[id]

symbol = SymbolTable()