	.file	"<stdin>"
	.intel_syntax noprefix
	.text
	.p2align 4
	.globl	write_low
	.type	write_low, @function
write_low:
.LFB0:
	.cfi_startproc
	prefetchw	[rdi]
	ret
	.cfi_endproc
.LFE0:
	.size	write_low, .-write_low
	.p2align 4
	.globl	write_high
	.type	write_high, @function
write_high:
.LFB1:
	.cfi_startproc
	prefetchw	[rdi]
	ret
	.cfi_endproc
.LFE1:
	.size	write_high, .-write_high
	.p2align 4
	.globl	read_low
	.type	read_low, @function
read_low:
.LFB2:
	.cfi_startproc
	prefetcht2	[rdi]
	ret
	.cfi_endproc
.LFE2:
	.size	read_low, .-read_low
	.p2align 4
	.globl	read_high
	.type	read_high, @function
read_high:
.LFB3:
	.cfi_startproc
	prefetcht0	[rdi]
	ret
	.cfi_endproc
.LFE3:
	.size	read_high, .-read_high
	.section	.note.GNU-stack,"",@progbits
