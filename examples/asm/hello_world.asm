; HELLO WORLD
welcome_len: 	WORD 	0xD
welcome:	WORD	"Hello, World!"
cnt:	WORD	?
pntr:	WORD	?

START:	CLA
	ST	cnt
	LD 	$welcome
	ST	pntr

LOOP:	LD	cnt
	INC
	CMP	welcome_len
	JZ	END
	ST	cnt

	LD	(pntr)
	OUT	0x1

	LD	pntr
	INC
	ST 	pntr
	JMP 	LOOP

END:	HLT




