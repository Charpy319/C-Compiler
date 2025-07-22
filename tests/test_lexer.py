import unittest
from core.lexer import Lexer as lexer

class TestLexer(unittest.TestCase):
    def test_declaration(self):
        code = "return 319; x++"
        tokens = lexer(code).tokenise()
        expected = ["RETURN", "INT_LITERAL", "SEMICOLON", "ID", "INCREMENT"]
        self.assertEqual([t.type.name for t in tokens], expected)

    def test_empty_input(self):
        code = ""
        tokens = lexer(code).tokenise()
        self.assertEqual(tokens, [])

if __name__ == "__main__":
    unittest.main()