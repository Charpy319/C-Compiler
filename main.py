import os
import sys
from core.compile import compile

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <c_file>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"Error: File '{path}' not found")
        sys.exit(1)

    with open(path, "r") as file:
        text = file.read()

    source = compile(text)
    print(source)

if __name__ == "__main__":
    main()