# C-Compiler
I will be learning to create my own C compiler.

The compiler is made up of three parts: lexer, parser and code generator.
The lexer takes the file and performs a regex and creates a list of tokens.
The parser creates an abstract syntax tree (AST) from the list of tokens with the program as the root.
The code generator takes in the AST and creates the assembly code from it.
Pretty printing prints out the AST in a more readable way


Lexer:
The lexer matches patterns for each TokenType to each token in the C file. Tokens range from keywords such as int to semicolons to whitespaces. 

The first step is to write out all the available tokens and their patterns. The patterns are then joined together into a string and using the re library, they are compiled into a pattern where they can be matched with the tokens in the C file.

An iterator is used to find all the matches and these are stored in a Token dataclass which contains the TokenType, the value and the line it was from.

Parser:
The parser then creates the AST from the list of tokens. The nodes of the AST are defined in dataclasses which contains the relationship between each node. The parser goes through the list of tokens and checks if the tokens fit a valid C program. If not, it raises a SyntaxError.

The Program is the root node and its children are the Functions. Functions contains statements which then contain Expressions within them. 

At each node, it checks if the syntax is correct and builds on the AST. The AST only contains the most important iformation so brackets and semicolons etc. are ommited.

Code generator:
With the AST, the code generator then writes out the tree in Assembly. 