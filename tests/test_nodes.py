import unittest
from core.data.nodes import AddSub, IntLiteral

class TestASTNodes(unittest.TestCase):
    def test_addsub_node(self):
        left = IntLiteral(3)
        right = IntLiteral(4)
        node = AddSub('+', left, right)
        self.assertEqual(node.operator, '+')
        self.assertEqual(node.operand1.value, 3)
        self.assertEqual(node.operand2.value, 4)

if __name__ == '__main__':
    unittest.main()