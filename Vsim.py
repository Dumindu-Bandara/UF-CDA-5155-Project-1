"""
UFID: 61994080
Name: Dumindu Ashen Bandara Elamure Mudiyanselage
Course: CDA 5155 - Computer Architecture
Project 1 - RISC-V Simulator
Date: 2024-10-11

Academic Honesty Statement:
On my honor, I have neither given nor received any unauthorized aid on this assignment.
"""

import argparse
from enum import Enum
import textwrap

MEMORY_START = 256


class DissasemblyState(Enum):
    INSTRUCTION = 1
    DATA = 2


class InstructionCategory(Enum):
    CATEGORY_1 = "00"
    CATEGORY_2 = "01"
    CATEGORY_3 = "10"
    CATEGORY_4 = "11"


class Category1Opcode(Enum):
    BEQ = "00000"
    BNE = "00001"
    BLT = "00010"
    SW = "00011"


class Category2Opcode(Enum):
    ADD = "00000"
    SUB = "00001"
    AND = "00010"
    OR = "00011"


class Category3Opcode(Enum):
    ADDI = "00000"
    ANDI = "00001"
    ORI = "00010"
    SLLI = "00011"
    SRAI = "00100"
    LW = "00101"


class Category4Opcode(Enum):
    JAL = "00000"
    BREAK = "11111"


def twos_complement(bin_str: str) -> int:
    value = -int(bin_str[0]) * 2 ** (len(bin_str) - 1) + int(bin_str[1:], 2)
    return value


def instruction_decoder(instruction: str, address: int):
    output_dict = {}

    if instruction[30:32] == InstructionCategory.CATEGORY_1.value:
        opcode = instruction[25:30]
        immediate = instruction[0:7] + instruction[20:25]

        output_dict["immediate"] = twos_complement(immediate)
        output_dict["rs1"] = int(instruction[12:17], 2)
        output_dict["rs2"] = int(instruction[7:12], 2)
        output_dict["func3"] = "000"

        output_dict["category"] = InstructionCategory.CATEGORY_1
        operation = Category1Opcode(opcode)
        output_dict["operation"] = operation

        if operation == Category1Opcode.SW:
            output_dict["assembly"] = (
                f"{instruction}\t{address}\t{operation.name.lower()} x{output_dict['rs1']}, {output_dict['immediate']}(x{output_dict['rs2']})"
            )
        else:
            output_dict["assembly"] = (
                f"{instruction}\t{address}\t{operation.name.lower()} x{output_dict['rs1']}, x{output_dict['rs2']}, #{output_dict['immediate']}"
            )

    elif instruction[30:32] == InstructionCategory.CATEGORY_2.value:
        opcode = instruction[25:30]
        output_dict["rd"] = int(instruction[20:25], 2)
        output_dict["rs1"] = int(instruction[12:17], 2)
        output_dict["rs2"] = int(instruction[7:12], 2)
        output_dict["func3"] = "000"
        output_dict["func7"] = "0000000"

        output_dict["category"] = InstructionCategory.CATEGORY_2
        operation = Category2Opcode(opcode)
        output_dict["operation"] = operation

        output_dict["assembly"] = (
            f"{instruction}\t{address}\t{operation.name.lower()} x{output_dict['rd']}, x{output_dict['rs1']}, x{output_dict['rs2']}"
        )

    elif instruction[30:32] == InstructionCategory.CATEGORY_3.value:
        opcode = instruction[25:30]
        output_dict["rd"] = int(instruction[20:25], 2)
        output_dict["rs1"] = int(instruction[12:17], 2)

        if opcode in [Category3Opcode.SLLI.value, Category3Opcode.SRAI.value]:
            immediate = instruction[7:12]
            output_dict["immediate"] = int(immediate, 2)
        else:
            immediate = instruction[0:12]
            output_dict["immediate"] = twos_complement(immediate)

        output_dict["func3"] = "000"

        output_dict["category"] = InstructionCategory.CATEGORY_3
        operation = Category3Opcode(opcode)
        output_dict["operation"] = operation

        if operation == Category3Opcode.LW:
            output_dict["assembly"] = (
                f"{instruction}\t{address}\t{operation.name.lower()} x{output_dict['rd']}, {output_dict['immediate']}(x{output_dict['rs1']})"
            )
        else:
            output_dict["assembly"] = (
                f"{instruction}\t{address}\t{operation.name.lower()} x{output_dict['rd']}, x{output_dict['rs1']}, #{output_dict['immediate']}"
            )

    elif instruction[30:32] == InstructionCategory.CATEGORY_4.value:
        opcode = instruction[25:30]

        output_dict["category"] = InstructionCategory.CATEGORY_4
        operation = Category4Opcode(opcode)
        output_dict["operation"] = operation

        if opcode == Category4Opcode.BREAK.value:
            output_dict["assembly"] = f"{instruction}\t{address}\tbreak"
        elif opcode == Category4Opcode.JAL.value:
            rd = int(instruction[20:25], 2)
            output_dict["rd"] = rd

            immediate = instruction[0:20]
            output_dict["immediate"] = twos_complement(immediate)
            output_dict["assembly"] = (
                f"{instruction}\t{address}\tjal x{output_dict['rd']}, #{output_dict['immediate']}"
            )

    return output_dict


class Disassembler:
    def __init__(self):
        self.memory = {}
        self.state = DissasemblyState.INSTRUCTION

    def disassemble(self, riscv_text: str):
        disassebly_output = []

        with open(riscv_text, "r") as file:
            instructions = file.readlines()

            address = MEMORY_START
            for instruction in instructions:
                instruction = instruction.strip()

                if self.state == DissasemblyState.INSTRUCTION:
                    decoded_instruction = instruction_decoder(instruction, address)
                    disassebly_output.append(decoded_instruction["assembly"])

                    if decoded_instruction["operation"] == Category4Opcode.BREAK:
                        self.state = DissasemblyState.DATA

                elif self.state == DissasemblyState.DATA:
                    data_value = twos_complement(instruction)
                    self.memory[address] = data_value
                    disassebly_output.append(f"{instruction}\t{address} {data_value}")

                address += 4

        with open("disassembly.txt", "w") as outfile:
            for line in disassebly_output:
                outfile.write(line + "\n")


class Processor:
    def __init__(self, memory=None):
        self.memory = memory if memory is not None else {}
        self.register_file = [0] * 32
        self.cycle = 1
        self.PC = MEMORY_START

    def process(self, riscv_text: str = None):
        with open(riscv_text, "r") as file:
            instructions = file.readlines()

            instructions = {
                MEMORY_START + i * 4: inst.strip()
                for i, inst in enumerate(instructions)
            }

        with open("simulation.txt", "w") as simfile:
            while True:
                instruction = instructions.get(self.PC)
                decoded_instruction = instruction_decoder(instruction, self.PC)

                self.execute_instruction(decoded_instruction)

                output_state = self.output_state(decoded_instruction)

                if self.cycle != 1:
                    simfile.write("\n")

                simfile.write(output_state)

                if decoded_instruction["operation"] == Category4Opcode.BREAK:
                    break

                self.cycle += 1

    def handle_overflow(self) -> None:
        for i in range(len(self.register_file)):
            if self.register_file[i] < -(2**31):
                self.register_file[i] = (
                    (self.register_file[i] + 2**31) % 2**32
                ) - 2**31
            elif self.register_file[i] > 2**31 - 1:
                self.register_file[i] = (
                    (self.register_file[i] - 2**31) % 2**32
                ) - 2**31
        return self.register_file

    def execute_instruction(self, decoded_instruction: dict):
        # print(decoded_instruction["category"], decoded_instruction["operation"])

        # NOTE: Check data ranges of output and immediates.

        if decoded_instruction["category"] == InstructionCategory.CATEGORY_1:
            if decoded_instruction["operation"] == Category1Opcode.BEQ:
                if (
                    self.register_file[decoded_instruction["rs1"]]
                    == self.register_file[decoded_instruction["rs2"]]
                ):
                    self.PC += decoded_instruction["immediate"] << 1
                else:
                    self.PC += 4

            elif decoded_instruction["operation"] == Category1Opcode.BNE:
                if (
                    self.register_file[decoded_instruction["rs1"]]
                    != self.register_file[decoded_instruction["rs2"]]
                ):
                    self.PC += decoded_instruction["immediate"] << 1
                else:
                    self.PC += 4

            elif decoded_instruction["operation"] == Category1Opcode.BLT:
                if (
                    self.register_file[decoded_instruction["rs1"]]
                    < self.register_file[decoded_instruction["rs2"]]
                ):
                    self.PC += decoded_instruction["immediate"] << 1
                else:
                    self.PC += 4

            elif decoded_instruction["operation"] == Category1Opcode.SW:
                address = (
                    self.register_file[decoded_instruction["rs2"]]
                    + decoded_instruction["immediate"]
                )
                self.memory[address] = self.register_file[decoded_instruction["rs1"]]
                self.PC += 4

        elif decoded_instruction["category"] == InstructionCategory.CATEGORY_2:
            if decoded_instruction["operation"] == Category2Opcode.ADD:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    + self.register_file[decoded_instruction["rs2"]]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category2Opcode.SUB:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    - self.register_file[decoded_instruction["rs2"]]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category2Opcode.AND:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    & self.register_file[decoded_instruction["rs2"]]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category2Opcode.OR:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    | self.register_file[decoded_instruction["rs2"]]
                )
                self.PC += 4

        elif decoded_instruction["category"] == InstructionCategory.CATEGORY_3:
            if decoded_instruction["operation"] == Category3Opcode.ADDI:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    + decoded_instruction["immediate"]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category3Opcode.ANDI:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    & decoded_instruction["immediate"]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category3Opcode.ORI:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    | decoded_instruction["immediate"]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category3Opcode.SLLI:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    << decoded_instruction["immediate"]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category3Opcode.SRAI:
                self.register_file[decoded_instruction["rd"]] = (
                    self.register_file[decoded_instruction["rs1"]]
                    >> decoded_instruction["immediate"]
                )
                self.PC += 4

            elif decoded_instruction["operation"] == Category3Opcode.LW:
                address = (
                    self.register_file[decoded_instruction["rs1"]]
                    + decoded_instruction["immediate"]
                )
                self.register_file[decoded_instruction["rd"]] = self.memory.get(
                    address, 0
                )
                self.PC += 4

        elif decoded_instruction["category"] == InstructionCategory.CATEGORY_4:
            if decoded_instruction["operation"] == Category4Opcode.JAL:
                self.register_file[decoded_instruction["rd"]] = self.PC + 4
                self.PC += decoded_instruction["immediate"] << 1

            elif decoded_instruction["operation"] == Category4Opcode.BREAK:
                self.PC += 4

        self.handle_overflow()

        # NOTE: x0 is always 0
        self.register_file[0] = 0  # x0 is always 0

    def output_state(self, decoded_instruction):
        memory_print = ""
        mem_addresses = sorted(self.memory.keys())

        if len(mem_addresses) > 0:
            mem_addresses_min = mem_addresses[0]
            mem_addresses_max = mem_addresses[-1]

            for i in range(mem_addresses_min, mem_addresses_max + 1, 32):
                row = [
                    self.memory.get(addr, 0)
                    for addr in range(i, i + 32, 4)
                    if addr <= mem_addresses_max
                ]

                memory_print += f"{i}:\t" + "\t".join([str(val) for val in row]) + "\n"
        else:
            memory_print = ""

        assembly_line = "\t".join(decoded_instruction["assembly"].split("\t")[1:])

        output = (
            textwrap.dedent("""
            {}
            Cycle {}:\t{}
            Registers
            x00:\t{}
            x08:\t{}
            x16:\t{}
            x24:\t{}
            Data
        """).format(
                "-" * 20,
                self.cycle,
                assembly_line,
                "\t".join(str(self.register_file[i]) for i in range(0, 8)),
                "\t".join(str(self.register_file[i]) for i in range(8, 16)),
                "\t".join(str(self.register_file[i]) for i in range(16, 24)),
                "\t".join(str(self.register_file[i]) for i in range(24, 32)),
            )
            + memory_print
        )

        return output[1:-1]


def main():
    parser = argparse.ArgumentParser(description="RISC-V Simulator")
    parser.add_argument(
        "riscv_text",
        type=str,
        help="Path to the input file containing assembly instructions",
    )

    args = parser.parse_args()
    riscv_text = args.riscv_text

    disassembler = Disassembler()
    disassembler.disassemble(riscv_text=riscv_text)

    processor = Processor(memory=disassembler.memory)
    processor.process(riscv_text=riscv_text)


if __name__ == "__main__":
    main()
