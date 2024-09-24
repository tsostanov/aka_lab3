; HELLO_USERNAME

START:	CLA
	ST	buf_len
	LD	$greet_str
	ST	buf_ptr

greet_loop:	LD	buf_len
	CMP	greet_ln
	JZ	ask
	INC
	ST	buf_len

	LD	(buf_ptr)
	OUT	0x1

	LD	buf_ptr
	INC
	ST	buf_ptr
	JMP 	greet_loop

ask:	LD	$hello_str
	ADD	hello_len
	ST	buf_ptr
	IN	0x2
	ST	buf_len
	ADD	hello_len
	ST	hello_len

ask_loop:	LD	buf_len
	JZ	welcome
	DEC
	ST	buf_len

	IN	0x2
	ST	(buf_ptr)

	LD	buf_ptr
	INC
	ST	buf_ptr
	JMP	ask_loop

welcome:	CLA
	ST	buf_len
	LD	$hello_str
	ST	buf_ptr

welcome_loop:	LD	buf_len
	CMP	hello_len
	JZ	end
	INC
	ST	buf_len

	LD	(buf_ptr)
	OUT	0x1

	LD	buf_ptr
	INC
	ST	buf_ptr
	JMP 	welcome_loop

end:	HLT




buf_len:	WORD	?
buf_ptr:	WORD	?
greet_ln:	WORD	0x12
greet_str:	WORD	"What is your name?"
hello_len:	WORD	0x7
hello_str:	WORD 	"Hello, "