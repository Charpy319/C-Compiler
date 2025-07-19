import os
import subprocess
import sys

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator 

if len(sys.argv) < 2:
    print("Usage: python3 compile.py <c_file>")
    sys.exit(1)

with open(sys.argv[1], "r") as file:
    text = file.read()

l = Lexer(text)
tokens = l.tokenise()

p = Parser(tokens)
ast = p.parse_program()

c = CodeGenerator(ast)
assembly = c.generate_program()

with open("main.s", "w") as file:
    file.write(assembly)

subprocess.run(["clang", "main.s", "-o", "main"])

result = subprocess.run(["./main"])
print("Program exited with: ", result.returncode)

if os.path.exists("main.s"):
    os.remove("main.s")

if os.path.exists("main"):
    os.remove("main")