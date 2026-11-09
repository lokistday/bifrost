# x86-64 System V AMD64; unsigned int trace_steps(unsigned int x)
.text
.globl trace_steps
.type trace_steps, @function
trace_steps:
    movl %edi, %eax
    addl $3, %eax
    cmpl $10, %eax
    jbe .Lsmall
    subl $2, %eax
    ret
.Lsmall:
    xorl $1, %eax
    ret
.size trace_steps, .-trace_steps
.section .note.GNU-stack,"",@progbits
