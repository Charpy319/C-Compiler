.section __TEXT,__text
.globl   _main
_main:
    pushq    %rbp
    movq    %rsp, %rbp
    subq    $16, %rsp
    movq    $11, %rax
    movq    %rax, -8(%rbp)
    subq    $16, %rsp
    movq    $10, %rax
    movq    %rax, -16(%rbp)
    movq    -8(%rbp), %rax
    movq    %rbp, %rsp
    popq    %rbp
    ret
