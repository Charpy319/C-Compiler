.section __TEXT,__text
    .globl   _main
_main:
    pushq    %rbp
    movq    %rsp, %rbp
_start1:
    movq    $1, %rax
    cmpq    $0, %rax
    je    _end1
    movq    $3, %rax
_cont1:
    jmp    _start1
_end1:
    movq    $0, %rax
    movq    %rbp, %rsp
    popq    %rbp
    ret
