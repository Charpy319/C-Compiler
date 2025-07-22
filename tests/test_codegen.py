import unittest
from core.codegen import CodeGenerator as gen
from core.data.nodes import IntLiteral, AddSub, Program, Function, Return

class TestCodeGen(unittest.TestCase):

    def test_input(self):
        tree = Program(
            function=Function(
                name="main",
                body=[Return(exp=AddSub('+', IntLiteral(1), IntLiteral(2)))]
                )
            )
        

        output = gen(tree).generate_program()
        expected = (
            ".section __TEXT,__text\n"
            ".globl   _main\n"
            "_main:\n"
            "    pushq    %rbp\n"
            "    movq    %rsp, %rbp\n"
            "    movq    $1, %rax\n"
            "    pushq    %rax\n"
            "    movq    $2, %rax\n"
            "    popq    %rcx\n"
            "    addq    %rcx, %rax\n"
            "    movq    %rbp, %rsp\n"
            "    popq    %rbp\n"
            "    ret\n"
        )
        self.assertIn(expected, output)

        

if __name__ == "__main__":
    unittest.main()