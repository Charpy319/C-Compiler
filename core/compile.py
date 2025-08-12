from .lexer import Lexer as lexer
from .parser import Parser as parser
from .fold import Fold as fold
from .codegen import CodeGenerator as codegen
from core.util.error import error

import os
import subprocess

def compile(text):
    print("Undergoing lexical analysis...\n")
    tokens = lexer(text).tokenise()
    error.display("Lexing")

    print("...and parsing...\n")
    ast = parser(tokens).parse_program()
    error.display("Parsing")

    print("...folding an optimizing...\n")
    folded = fold(ast).start_fold()

    print("...and generating the assembly\n")
    assembly = codegen(folded).generate_program()
    error.display("Code generation")

    with open("main.s", "w") as file:
        file.write(assembly)

    subprocess.run(["clang", "main.s", "-o", "main"])

    result = subprocess.run(["./main"])

    if os.path.exists("main.s"):
        os.remove("main.s")

    if os.path.exists("main"):
        os.remove("main")

    return f"Program exited with: {result.returncode}"