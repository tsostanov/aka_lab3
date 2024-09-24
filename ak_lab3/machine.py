import argparse
import logging
from collections import deque
from enum import StrEnum, auto

from ak_lab3.isa import Instruction, Opcode, Argtype, read_code

DATA_MEMORY_SIZE = 1024


class AluOperation(StrEnum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    XOR = auto()
    NOT = auto()
    INC = auto()
    DEC = auto()


opcode_to_alu_op: dict[Opcode, AluOperation] = {
    Opcode.ADD: AluOperation.ADD,
    Opcode.SUB: AluOperation.SUB,
    Opcode.MUL: AluOperation.MUL,
    Opcode.DIV: AluOperation.DIV,
    Opcode.XOR: AluOperation.XOR,
    Opcode.NOT: AluOperation.NOT,
    Opcode.INC: AluOperation.INC,
    Opcode.DEC: AluOperation.DEC,
}


class ALU:

    def __init__(self):
        self._z_flag = False

    def perform(self, left: int, right: int, operation: AluOperation) -> int:
        output_value: int
        match operation:
            case AluOperation.ADD:
                output_value = left + right
            case AluOperation.SUB:
                output_value = right - left
            case AluOperation.MUL:
                output_value = left * right
            case AluOperation.DIV:
                output_value = left // right
            case AluOperation.XOR:
                output_value = left ^ right
            case AluOperation.NOT:
                output_value = ~left
            case AluOperation.INC:
                output_value = left + 1
            case AluOperation.DEC:
                output_value = left - 1
            case _:
                raise NotImplementedError()
        self._z_flag = output_value == 0
        return output_value

    @property
    def z_flag(self) -> bool:
        return self._z_flag


class IO:
    def __init__(self, input_buffer: list[int], is_numeric_io: bool):
        self.is_int_io = is_numeric_io
        self.output = ""
        self.input_buffer = deque(input_buffer)
        self.input_buffer.appendleft(len(input_buffer))

    def write_byte(self, b: int):
        if self.is_int_io:
            self.output += str(b)
        elif b == 0:
            self.output += "\n"
        else:
            self.output += chr(b)

    def read_byte(self) -> int:
        if len(self.input_buffer) == 0:
            raise EOFError("Input is over")
        return self.input_buffer.popleft()

    def __repr__(self) -> str:
        return f"{map(chr, self.input_buffer)}, {self.output}"


class IOController:
    def __init__(self, ios: dict[int, IO]):
        self.ios = ios

    def write_io(self, port: int, data: int):
        assert port in self.ios, "No such io port!"
        self.ios[port].write_byte(data)

    def read_io(self, port: int) -> int:
        assert port in self.ios, "No such io port!"
        return self.ios[port].read_byte()

    def __repr__(self) -> str:
        return "\n".join(f"{port}: {io}" for port, io in self.ios.items())


class DataPath:
    pc: int = 0
    ar: int = 0
    ac: int = 0

    def __init__(
        self, alu: ALU, io_controller: IOController, program: list[Instruction]
    ):
        self.alu = alu
        self.io_controller = io_controller
        self.memory = program + [0] * (DATA_MEMORY_SIZE - len(program))

    def signal_read_memory(self) -> Instruction | int:
        instruction = self.memory[self.ar]
        if isinstance(instruction, Instruction):
            if instruction.opcode == Opcode.WORD:
                assert (
                    instruction.arg is not None
                ), "WORD with None argument! Check translator"
                assert isinstance(instruction.arg, int)
                return instruction.arg
        return instruction

    def signal_write_memory(self, value: int):
        self.memory[self.ar] = value

    def signal_latch_ac(self, value: int):
        self.ac = value

    def signal_latch_pc(self, value: int):
        self.pc = value

    def signal_latch_ar(self, value: int):
        self.ar = value

    def perform_alu_operation(self, alu_operation: AluOperation, right: int) -> int:
        return self.alu.perform(self.ac, right, alu_operation)


class ControlUnit:
    _tick: int
    no_op_instruction_set = (
        Opcode.CLA,
        Opcode.INC,
        Opcode.DEC,
        Opcode.HLT,
        Opcode.NOT,
        Opcode.NEG,
    )

    def __init__(self, data_path: DataPath):
        self.data_path = data_path
        self._tick = 0

    def tick(self):
        self._tick += 1

    def current_tick(self):
        return self._tick

    def initialize_datapath(self, start: int):
        self.data_path.signal_latch_pc(start)

    def decode_and_execute_instruction(self):
        self.data_path.signal_latch_ar(self.data_path.pc)
        self.tick()
        instruction = self.data_path.signal_read_memory()
        assert isinstance(instruction, Instruction), "Executing data!"
        self.tick()
        self.data_path.signal_latch_pc(self.data_path.pc + 1)
        self.tick()
        if instruction.opcode in self.no_op_instruction_set:
            match instruction.opcode:
                case Opcode.CLA:
                    self.execute_cla()
                case Opcode.HLT:
                    self.execute_hlt()
                case Opcode.INC | Opcode.DEC | Opcode.NOT | Opcode.NEG:
                    self.execute_no_op_alu_operation(instruction.opcode)
                case _:
                    raise NotImplementedError()
        else:
            if instruction.opcode in (Opcode.JMP, Opcode.JZ):
                arg = self.parse_instruction_arg_for_jump(
                    instruction.arg_type, instruction.arg
                )
            else:
                arg = self.parse_instruction_arg(instruction.arg_type, instruction.arg)
            assert isinstance(arg, int), "Argument must be not instruction"
            match instruction.opcode:
                case Opcode.ST:
                    self.execute_st()
                case Opcode.LD:
                    self.execute_ld(arg)
                case Opcode.CMP:
                    self.execute_cmp(arg)
                case Opcode.JZ:
                    self.execute_jz(arg)
                case Opcode.JMP:
                    self.execute_jmp(arg)
                case Opcode.IN:
                    self.execute_in(arg)
                case Opcode.OUT:
                    self.execute_out(arg)
                case (
                    Opcode.DIV
                    | Opcode.MUL
                    | Opcode.ADD
                    | Opcode.SUB
                    | Opcode.AND
                    | Opcode.OR
                    | Opcode.XOR
                ):
                    self.execute_alu_operation(
                        opcode_to_alu_op[instruction.opcode], arg
                    )
                case _:
                    raise NotImplementedError()

    def parse_instruction_arg(self, argtype: Argtype, arg: int) -> int | Instruction:
        if argtype is None:
            return arg
        if argtype == Argtype.DIRECT_ADDRESS:
            self.data_path.signal_latch_ar(arg)
            self.tick()
            return self.data_path.signal_read_memory()
        if argtype == Argtype.RELATIVE_ADDRESS:
            self.data_path.signal_latch_ar(arg)
            self.tick()
            data = self.data_path.signal_read_memory()
            assert isinstance(data, int), "Argument must be int"
            self.data_path.signal_latch_ar(data)
            self.tick()
            return self.data_path.signal_read_memory()
        if argtype == Argtype.DIRECT_LOAD:
            return arg
        raise NotImplementedError()

    def parse_instruction_arg_for_jump(self, argtype: Argtype, arg: int) -> int | Instruction:
        if argtype is None:
            return arg
        if argtype == Argtype.DIRECT_ADDRESS:
            return arg
        if argtype == Argtype.RELATIVE_ADDRESS:
            self.data_path.signal_latch_ar(arg)
            self.tick()
            return self.data_path.signal_read_memory()
        if argtype == Argtype.DIRECT_LOAD:
            return arg
        raise NotImplementedError()

    def execute_cla(self):
        self.data_path.signal_latch_ac(0)
        self.tick()

    def execute_no_op_alu_operation(self, opcode: Opcode):
        if opcode == Opcode.NEG:
            self.execute_no_op_alu_operation(Opcode.NOT)
            self.execute_no_op_alu_operation(Opcode.INC)
            return
        alu_operation: AluOperation = opcode_to_alu_op[opcode]
        self.data_path.signal_latch_ac(
            self.data_path.perform_alu_operation(alu_operation, 0)
        )
        self.tick()

    def execute_st(self):
        self.data_path.signal_write_memory(
            self.data_path.perform_alu_operation(AluOperation.ADD, 0)
        )
        self.tick()

    def execute_ld(self, arg: int):
        self.data_path.signal_latch_ac(0)
        self.tick()
        self.data_path.signal_latch_ac(
            self.data_path.perform_alu_operation(AluOperation.ADD, arg)
        )
        self.tick()

    def execute_cmp(self, arg: int):
        self.data_path.perform_alu_operation(AluOperation.SUB, arg)
        self.tick()

    def execute_jz(self, arg: int):
        if self.data_path.alu.z_flag:
            self.data_path.signal_latch_pc(arg)
        self.tick()

    def execute_jmp(self, arg: int):
        self.data_path.signal_latch_pc(arg)
        self.tick()

    def execute_in(self, arg: int):
        self.data_path.signal_latch_ac(self.data_path.io_controller.read_io(arg))
        self.tick()

    def execute_out(self, arg: int):
        self.data_path.io_controller.write_io(
            arg, self.data_path.perform_alu_operation(AluOperation.ADD, 0)
        )
        self.tick()

    def execute_alu_operation(self, alu_operation: AluOperation, arg: int):
        self.data_path.signal_latch_ac(
            self.data_path.perform_alu_operation(alu_operation, arg)
        )
        self.tick()

    def execute_hlt(self):
        raise StopIteration

    def __repr__(self):
        state_repr = (
            f"TICK: {self.current_tick():4} "
            f"PC: {self.data_path.pc:4} "
            f"AR: {self.data_path.ar:4} "
            f"AC: {self.data_path.ac:4} "
            f"Z_FLAG: {self.data_path.alu.z_flag:1} "
        )
        instr_repr = str(self.data_path.memory[self.data_path.pc])

        return f"{state_repr} \t{instr_repr:32} "


def simulation(code_raw: dict, input_tokens, is_int_io, limit) -> tuple[int, int]:
    alu = ALU()
    output_io = IO([], is_int_io)
    input_io = IO(input_tokens, is_int_io)
    io_controller = IOController(
        {
            1: output_io,
            2: input_io,
        }
    )
    code = list(map(Instruction.from_dict, code_raw["code"]))
    data_path = DataPath(alu, io_controller, code)
    control_unit = ControlUnit(data_path)
    control_unit.initialize_datapath(code_raw["start"])
    instr_counter = 0
    logging.debug("%s", control_unit)
    try:
        while instr_counter < limit:
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug("%s", control_unit)
    except EOFError:
        logging.warning("Input buffer is empty!")
    except StopIteration:
        pass

    if instr_counter >= limit:
        logging.warning("Limit exceeded!")
    logging.info("output buffer: %s", output_io.output)
    return instr_counter, control_unit.current_tick()


def main(code_filename: str, input_filename: str, is_int_io: str):
    code = read_code(code_filename)
    with open(input_filename, encoding="utf-8") as file:
        input_text = file.read()
        input_token = list(map(ord, input_text))
    instr_counter, ticks = simulation(code, input_token, is_int_io, limit=1000)
    logging.info("instr_counter: %d", instr_counter)
    logging.info("ticks: %d", ticks)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(description="Machine")
    parser.add_argument(
        "--iotype",
        type=str,
        nargs="?",
        help='"int" for int io output and str for str io output',
        default="str",
    )
    parser.add_argument("input_file", type=str, nargs=1, help="input_file")
    parser.add_argument("output_file", type=str, nargs=1, help="output_file")
    args = parser.parse_args()
    main(args.input_file[0], args.output_file[0], args.iotype == "int")
