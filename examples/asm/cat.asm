; cat
cnt:	WORD	?

START:	IN	0x2
	ST	cnt

LOOP:	LD	cnt
	JZ	END
	DEC
	ST	cnt
	IN	0x2
	OUT	0x1
	JMP	LOOP

END:	HLT