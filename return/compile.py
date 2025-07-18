"""
This is the first compiler I will write for c which just handles a return. 
The steps are:
1. lexer
2. parser
3. code generator
"""

"""
First step is to write a lexer. To do this, I will need to use regex to match tokens. 
The lexer matches the code to token types and returns a list.
In python, the "re" module is used.
Types can be stores in an enum class which basically numbers each type to make them more manageable.
The tokens are stored in a dataclass.
"""