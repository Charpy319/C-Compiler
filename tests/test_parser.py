import unittest
from core.parser import Parser as parser
from core.lexer import Lexer as lexer
from core.data.nodes import IntLiteral, UnOp

class TestParser(unittest.TestCase):
    def test_parse_int_literal(self):
        code = "42"
        tokens = lexer(code).tokenise()
        ast = parser(tokens).parse_fact()
        self.assertIsInstance(ast, IntLiteral)
        self.assertEqual(ast.value, 42)

    def test_parse_unary_op(self):
        code = "-5"
        tokens = lexer(code).tokenise()
        ast = parser(tokens).parse_fact()
        self.assertIsInstance(ast, UnOp)
        self.assertEqual(ast.operator, '-')
        self.assertEqual(ast.operand.value, 5)

if __name__ == '__main__':
    unittest.main()