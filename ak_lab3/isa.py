import json
from dataclasses import dataclass, asdict
from enum import StrEnum, auto, Enum
from typing import Optional


class Opcode(StrEnum):
    CLA = auto()
    INC = auto()
    DEC = auto()
    HLT = auto()
    NOT = auto()
    NEG = auto()
    ST = auto()
    LD = auto()
    CMP = auto()
    JZ = auto()
    JMP = auto()
    IN = auto()
    OUT = auto()
    DIV = auto()
    MUL = auto()
    ADD = auto()
    SUB = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    WORD = auto()


class Argtype(StrEnum):
    DIRECT_LOAD = auto()
    DIRECT_ADDRESS = auto()
    RELATIVE_ADDRESS = auto()


@dataclass
class Instruction:
    opcode: Opcode
    arg: Optional[int | str] = None
    arg_type: Optional[Argtype] = None

    def to_dict(self):
        data = asdict(self)
        return {key: value for key, value in data.items() if value is not None}

    @staticmethod
    def from_dict(data: dict):
        assert "opcode" in data, "Parsing Instruction failed! Check translator"
        return Instruction(
            data["opcode"],
            data["arg"] if "arg" in data else None,
            data["arg_type"] if "arg_type" in data else None,
        )

    def __str__(self) -> str:
        return str(self.to_dict())


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Instruction):
            return o.to_dict()
        if isinstance(o, Enum):
            return o.value
        return json.JSONEncoder.default(self, o)


def write_code(filename: str, code: dict) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, cls=CustomEncoder, indent=2))


def read_code(filename: str) -> dict[str, str]:
    return json.load(open(filename, encoding="utf-8"))
