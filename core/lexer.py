"""
First step is to write a lexer. To do this, I will need to use regex to self.match tokens. 
The lexer self.matches the code to token types and returns a list.
In python, the "re" module is used.
Types can be stores in an enum class which basically numbers each type to make them more manageable.
The tokens are stored in a dataclass.
"""
from core.data.token_types import *
from core.util.error import error
from typing import Optional

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.start = 0
        self.current = 0
        self.line = 1

        # A dict is used here to differentiate keywords from ID 
        self.keywords = {
            "int": TokenType.INT,
            "char": TokenType.CHAR,
            "float": TokenType.FLOAT,
            "void": TokenType.VOID,
            "return": TokenType.RETURN,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "for": TokenType.FOR,
            "while": TokenType.WHILE,
            "do": TokenType.DO,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE
        }
        self.whitespace = {' ', '\t', '\r', '\n', '\f', '\v'}
        self.punctuation = {
            '!', '%', '^', '&', '*', '(', ')', '-', '+', '=',
            '[', ']', '{', '}', '|', '\\', ';', ':', "'", '"',
            '<', '>', ',', '.', '/', '?'
        }
        self.tokens = []

    def at_end(self) -> bool:
        return self.current >= len(self.text)

    def peek(self) -> Optional[str]:
        return self.text[self.current] if not self.at_end() else None
    
    def peek_next() -> Optional[str]:
        self.current += 1
        if self.at_end():
            return None
        self.current -= 1
        return self.text[self.current + 1]

    def consume(self) -> Optional[str]:
        if self.at_end():
            return None
        now = self.text[self.current]
        self.current += 1
        return now

    def match(self, word) -> bool:
        self.peek()
        if self.at_end() or self.text[self.current] != word: 
            return False
        else:
            self.consume()
            return True
    
    # Finds end of id
    def identifier(self) -> None:
        while self.peek().isalnum() or self.peek() == '_':
            self.consume()
        return

    # Finds end of number and returns if it is a float
    def number(self) -> bool:
        dotted = False
        while self.peek().isdigit():
            c = self.consume()
            if not dotted and self.peek() == '.' and self.peek_next().isdigit():
                c = self.consume()
                dotted == True
        return dotted

    def make_str(self) -> str:
        s = ""
        for i in range(self.start, self.current):
            s += self.text[i]
        return s

    def ill_formed(self) -> bool:
        ill = False
        while self.peek() not in self.whitespace and self.peek() not in self.punctuation:
            ill = True
            self.consume()
        return ill

    def tokenise(self) -> list:
        if self.at_end():
            return self.tokens
        self.start = self.current
        c = self.consume()

        # Single characters
        if c == '{': self.tokens.append(Token(type=TokenType.OPEN_BRACE, line=self.line))
        elif c == '}': self.tokens.append(Token(type=TokenType.CLOSE_BRACE, line=self.line))
        elif c == '(': self.tokens.append(Token(type=TokenType.OPEN_PARENTHESIS, line=self.line))
        elif c == ')': self.tokens.append(Token(type=TokenType.CLOSE_PARENTHESIS, line=self.line))
        elif c == ';': self.tokens.append(Token(type=TokenType.SEMICOLON, line=self.line))
        elif c == ':': self.tokens.append(Token(type=TokenType.COLON, line=self.line))
        elif c == ',': self.tokens.append(Token(type=TokenType.COMMA, line=self.line))
        elif c == '?': self.tokens.append(Token(type=TokenType.QUESTION_MARK, line=self.line))
        elif c == '~': self.tokens.append(Token(type=TokenType.BIT_COMP, line=self.line))
        elif c == '.': self.tokens.append(Token(type=TokenType.DOT, line=self.line))

        # Compound characters
        elif c == '+':
            if self.match('+'):
                self.tokens.append(Token(type=TokenType.INCREMENT, line=self.line))
            elif self.match('='):
                self.tokens.append(Token(type=TokenType.ASSIGN_ADD, line=self.line))
            else:
                self.tokens.append(Token(type=TokenType.ADDITION, line=self.line))
        elif c == '-':
            if self.match('-'):
                self.tokens.append(Token(type=TokenType.DECREMENT, line=self.line))
            elif self.match('='):
                self.tokens.append(Token(type=TOkenType.ASSIGN_SUB, line=self.line))
            else:
                self.tokens.append(Token(type=TokenType.SUBTRACTION, line=self.line))
        elif c == '*':
            self.tokens.append(
                Token(type=TokenType.ASSIGN_MULT, line=self.line)
                if self.match('=') else
                Token(type=TokenType.MULTIPLICATION, line=self.line)
            )
        elif c == '/':
            if self.match('/'):
                while not self.at_end() and self.peek() != '\n': self.consume()
            elif self.match('*'):
                start_line = self.line
                while not self.at_end() and self.peek() != '*' and self.peek_next() != '/':
                    if self.peek() == '\n':
                        self.line += 1
                    self.consume()
                if self.at_end():
                    error.report(error_msg=f"Unterminated comment starting from {start_line}", line=start_line, type="IlligalSyntax")
            else:
                self.tokens.append(
                    Token(type=TokenType.ASSIGN_DIV, line = self.line)
                    if self.match('=') else
                    Token(type=TokenType.DIVISION, line=self.line)
                )
        elif c == '%':
            self.tokens.append(
                Token(type=TokenType.ASSIGN_MOD, line=self.line)
                if self.match('=') else
                Token(type=TokenType.MODULO, line=self.line)
            )
        elif c == '=':
            self.tokens.append(
                Token(type=TokenType.EQUAL, line=self.line)
                if self.match('=') else
                Token(type=TokenType.ASSIGNMENT, line=self.line)
            )
        elif c == '!':
            self.tokens.append(
                Token(type=TokenType.NOT_EQUAL, line=self.line)
                if self.match('=') else
                Token(type=TokenType.LOGICAL_NEGATION, line=self.line)
            )
        elif c == '<':
            if self.match('='):
                self.tokens.append(Token(type=TokenType.LESS_THAN_OR_EQUAL, line=self.line))
            elif self.match('<'):
                self.tokens.append(Token(type=TokenType.ASSIGN_LEFT_SHIFT, line=self.line)
                if self.match('=') else
                Token(type=TokenType.BIT_SHIFT_LEFT, line=self.line)
                )
            else:
                self.tokens.append(Token(type=TokenType.LESS_THAN, line=self.line))
        elif c == '>':
            if self.match('='):
                self.tokens.append(Token(type=TokenType.GREATER_THAN_OR_EQUAL, line=self.line))
            elif self.match('>'):
                self.tokens.append(Token(type=TokenType.ASSIGN_RIGHT_SHIFT, line=self.line)
                if self.match('=') else
                Token(type=TokenType.BIT_SHIFT_RIGHT, line=self.line)
                )
            else:
                self.tokens.append(Token(type=TokenType.GREATER_THAN, line=self.line))
        elif c == '&':
            if self.match('='):
                self.tokens.append(Token(type=TokenType.ASSIGN_ADD, line=self.line))
            elif self.match('&'):
                self.tokens.append(Token(type=TokenType.AND, line=self.line))
            else:
                self.tokens.append(Token(type=TokenType.BIT_AND, line=self.line))
        elif c == '|':
            if self.match('='):
                self.tokens.append(Token(type=TokenType.ASSIGN_OR, line=self.line))
            elif self.match('|'):
                self.tokens.append(Token(type=TokenType.OR, line=self.line))
            else:
                self.tokens.append(Token(type=TokenType.BIT_OR, line=self.line))
        elif c == '^':
            self.tokens.append(
                Token(type=TokenType.ASSIGN_BIT_XOR, line=self.line)
                if self.match('=') else
                Token(type=TokenType.BIT_XOR, line=self.line)
            )

        # Identifier
        elif not self.at_end() and c.isalpha():
            self.identifier()
            id = self.make_str()
            ill = self.ill_formed()
            if ill:
                ill_id = self.make_str()
                error.report(error_msg=f"Ill-formed identifier: {ill_id}", line=self.line, type="InvalidSyntax")
                self.tokens.append(Token(type=TokenType.ERROR, line=self.line))
            elif id in self.keywords:
                keyword = self.keywords[id]
                self.tokens.append(Token(type=keyword, line=self.line))
            else:
                self.tokens.append(Token(type=TokenType.ID, line=self.line, value=id))

        # Char - implement later

        # String
        elif c == '"':
            while not self.at_end() and self.peek().isalnum():
                self.consume()
            if self.at_end():
                error.report(error_msg="Non-terminated string", line=self.line, type="IlligalSyntax")
                self.tokens.append(Token(type=TokenType.ERROR, line=self.line))
            elif self.peek == '\n':
                error.report(error_msg="Invalid multiline string", line=self.line, type="IlligalSyntax")
                self.tokens.append(Token(type=TokenType.ERROR, line=self.line))
            else:
                s = self.make_str()
                self.tokens.append(Token(type=TokenType.STRING_LIT, line=self.line, value=s))
                self.consume()
        
        # Number
        elif not self.at_end() and c.isdigit():
            dotted = self.number()
            num = self.make_str()
            ill = self.ill_formed()
            while self.peek() == '.':   # '.' does not act as delimeter so need keep going
                self.consume()
                ill = self.ill_formed()
            if ill:
                ill_num = self.make_str()
                error.report(error_msg=f"Ill-formed number {ill_num}", line=self.line, type="InvalidSyntax")
                self.tokens.append(Token(type=TokenType.ERROR, line=self.line))
            elif dotted:
                self.tokens.append(Token(type=TokenType.FLOAT_LIT, line=self.line, value=num))
            else:
                self.tokens.append(Token(type=TokenType.INT_LITERAL, line=self.line, value=num))

        # Newline
        elif c == '\n':
            self.line += 1
        
        # Invalid characters
        else:
            if c not in self.whitespace:
                self.ill_formed()
                ill_string = self.make_str()
                error.report(error_msg=f"Ill-formed identifier {ill_string}", line=self.line, type="InvalidSyntax")
                self.tokens.append(Token(type=TokenType.ERROR, line=self.line))
        
        return self.tokenise()