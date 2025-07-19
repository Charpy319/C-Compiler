# C-Compiler

## Introduction

### About the project
This is actually my first project so I am very excited. Being at a lost of what to build, I went onto the build your own x and project based learning repos and I found this tutorial by [Nora Sandler](https://norasandler.com/). I have always been interested in working out how our technology works and writing a compiler is just really cool. Here is where I will document the different stages of building the compiler, as per the guide by Nora Sandler. So welcom here if your reading this and I hope this inspires you to build your own compiler as well.


## How a compiler works

### Components

#### Lexer:
The lexer matches patterns for each TokenType to each token in the C file. Tokens range from keywords such as int to semicolons to whitespaces. 

The first step is to write out all the available tokens and their patterns. The patterns are then joined together into a string and using the re library, they are compiled into a pattern where they can be matched with the tokens in the C file.

An iterator is used to find all the matches and these are stored in a Token dataclass which contains the TokenType, the value and the line it was from.

#### Parser:
The parser then creates the AST from the list of tokens. The nodes of the AST are defined in dataclasses which contains the relationship between each node. The parser goes through the list of tokens and checks if the tokens fit a valid C program. If not, it raises a SyntaxError.

The Program is the root node and its children are the Functions. Functions contains statements which then contain Expressions within them. 

At each node, it checks if the syntax is correct and builds on the AST. The AST only contains the most important iformation so brackets and semicolons etc. are ommited.

#### Code generator:
With the AST, the code generator then writes out the tree in Assembly. 

#### Pretty printing:
This prints out the AST in a more readable way which is useful for debugging.

## Next

Continue onto [stage 1](stage_1.md), the compiler for returning an integer.