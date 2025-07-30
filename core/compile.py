from .lexer import Lexer as lexer
from .parser import Parser as parser
from .codegen import CodeGenerator as codegen

import os
import subprocess

def compile(text):
    tokens = lexer(text).tokenise()
    ast = parser(tokens).parse_program()

    assembly = codegen(ast).generate_program()

    with open("main.s", "w") as file:
        file.write(assembly)

    subprocess.run(["clang", "main.s", "-o", "main"])

    result = subprocess.run(["./main"])

    """if os.path.exists("main.s"):
        os.remove("main.s")

    if os.path.exists("main"):
        os.remove("main")"""

    return f"Program exited with: {result.returncode}"