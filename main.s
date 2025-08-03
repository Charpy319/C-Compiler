.section __TEXT,__text
.globl   _main
_main:
    pushq    %rbp
    movq    %rsp, %rbp
    subq    $16, %rsp
    movq    $0, %rax
    movq    %rax, -8(%rbp)
    movq    $0, %rax
    movq    %rax, -16(%rbp)
    movq    -8(%rbp), %rax
    cmpq    $0, %rax
    je    _el1
    movq    $2, %rax
    movq    %rax, -8(%rbp)
    jmp    _end1
_el1:
    movq    $3, %rax
    movq    %rax, -8(%rbp)
_end1:
    movq    -16(%rbp), %rax
    cmpq    $0, %rax
    je    _el2
    movq    $4, %rax
    movq    %rax, -16(%rbp)
    jmp    _end2
_el2:
    movq    $5, %rax
    movq    %rax, -16(%rbp)
_end2:
    movq    -8(%rbp), %rax
    pushq    %rax
    movq    -16(%rbp), %rax
    popq    %rcx
    addq    %rcx, %rax
    movq    %rbp, %rsp
    popq    %rbp
    ret
