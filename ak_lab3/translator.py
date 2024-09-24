import argparse
from functools import reduce
from typing import AnyStr

from ak_lab3.isa import write_code, Opcode, Instruction, Argtype


def remove_comment(line: str) -> str:
    return line.split(";", 1)[0].strip()


def parse_opcode(code: str) -> Opcode:
    return Opcode[code]


def parse_word_data(data: str) -> list[Instruction]:
    if data.startswith("0x"):
        return [Instruction(Opcode.WORD, int(data[2:], 16))]
    if data == "?":
        return [Instruction(Opcode.WORD, 0)]
    assert data.count('"') > 1, "Wrong WORD format"
    return [Instruction(Opcode.WORD, ord(ch)) for ch in data.strip('"')]


def preprocess(input_data: AnyStr):
    data = [remove_comment(str(line_raw)) for line_raw in input_data.splitlines()]
    data = [line.replace("\t", " ") for line in data]
    data = [" ".join(line.split()) for line in data]
    data = [line for line in data if line != ""]
    return "\n".join(data)


def translate_stage_1(input_data: str) -> tuple[list[Instruction], dict[str, int]]:
    code: list[Instruction] = []
    labels: dict[str, int] = {}
    for line in input_data.splitlines():
        line_data: list[str] = line.split()
        if line_data[0].endswith(":"):
            labels.update({line_data[0][:-1]: len(code)})
            line_data.pop(0)
        if len(line_data) == 1:
            code.append(Instruction(parse_opcode(line_data[0])))
            continue
        line_data = [line_data[0], reduce(lambda x, y: x + " " + y, line_data[1:])]
        if line_data[0].lower() == "word":
            code += parse_word_data(line_data[1])
            continue
        if len(line_data) == 2:
            opcode = parse_opcode(line_data[0])
            instr: Instruction
            arg = line_data[1]
            if opcode in (Opcode.IN, Opcode.OUT):
                instr = Instruction(opcode, int(arg[2:], 16))
            elif arg[0] == "(" and arg[-1] == ")":
                instr = Instruction(opcode, arg[1:-1], Argtype.RELATIVE_ADDRESS)
            elif arg[0] == "$":
                instr = Instruction(opcode, arg[1:], Argtype.DIRECT_LOAD)
            elif arg[0] == "#":
                instr = Instruction(opcode, int(arg[3:], 16), Argtype.DIRECT_LOAD)
            else:
                instr = Instruction(opcode, arg, Argtype.DIRECT_ADDRESS)
            code.append(instr)
    return code, labels


def translate_stage_2(
    code: list[Instruction], labels: dict[str, int]
) -> tuple[list[Instruction], int]:
    for i, instr in enumerate(code):
        if instr.arg is None or instr.arg_type is None:
            continue
        if instr.arg_type == Argtype.DIRECT_LOAD and isinstance(instr.arg, int):
            continue
        assert code[i].arg in labels, f"None such label: {code[i].arg}"
        code[i].arg = labels[str(code[i].arg)]
    assert "START" in labels, "No label START in code!"
    return code, labels["START"]


def translate(code_raw: str) -> dict:
    code = preprocess(code_raw)
    code, labels = translate_stage_1(code)
    code, start = translate_stage_2(code, labels)
    return {
        "start": start,
        "code": code,
    }


def main(source_file: str, target_file: str):
    with open(source_file, "r", encoding="utf-8") as f:
        input_data = f.read()
    code = translate(input_data)
    write_code(target_file, code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translator")
    parser.add_argument("input_file", type=str, nargs=1, help="Input file")
    parser.add_argument("output_file", type=str, nargs=1, help="Output file")
    args = parser.parse_args()
    main(args.input_file[0], args.output_file[0])
