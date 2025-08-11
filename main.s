    .section __DATA,__data
    .globl    _foo
    .p2align    3
_foo:
    .int    3


    .zerofill __DATA,__bss,_foo,8,3


    .section __TEXT,__text
    .globl    _main
_main:
    pushq    %rbp
    movq    %rsp, %rbp
    movq    _foo(%rip), %rax
    movq    %rbp, %rsp
    popq    %rbp
    ret

