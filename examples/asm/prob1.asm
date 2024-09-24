; prob1
number:	WORD	0x3E7 ; 999
buf:	WORD	?
answer:	WORD	0x0
; prob1
START:	LD	number
	DIV	#0x3
	ST	buf
	INC
	MUL	buf
	DIV	#0x2
	MUL	#0x3
	ST	answer

	LD	number
	DIV	#0x5
	ST	buf
	INC
	MUL 	buf
	DIV	#0x2
	MUL	#0x5
	ADD 	answer
	ST 	answer

	LD	number
	DIV	#0xF
	ST	buf
	INC
	MUL 	buf
	DIV	#0x2
	MUL	#0xF
	NOT		; neg
	INC
	ADD	answer
	ST 	answer
	HLT
