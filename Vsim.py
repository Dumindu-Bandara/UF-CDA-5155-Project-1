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
    value = - int(bin_str[0]) * 2**(len(bin_str) - 1) + int(bin_str[1:], 2)
    return value
    


class Disassembler():

    def __init__(self, riscv_text: str):
        self.riscv_text = riscv_text
        self.memory = {}
        self.state = DissasemblyState.INSTRUCTION
        

    def disassemble(self, riscv_text: str):

        disassebly_output = []
        
        with open(riscv_text, 'r') as file:
            instructions = file.readlines()

            address = MEMORY_START
            for instruction in instructions:
                instruction = instruction.strip()

                if self.state == DissasemblyState.INSTRUCTION:
                    if instruction[30:32] == InstructionCategory.CATEGORY_1.value:
                        opcode = instruction[25:30]
                        immediate = instruction[0:7] + instruction[20:25]
                        immediate = twos_complement(immediate)
                        rs1 = int(instruction[12:17], 2)
                        rs2 = int(instruction[7:12], 2)
                        func3 = "000"

                        operation = Category1Opcode(opcode)

                        if operation == Category1Opcode.SW:
                            disassebly_output.append(f"{instruction}\t{address} {operation.name.lower()} x{rs1}, {immediate}(x{rs2})")
                        else:
                            disassebly_output.append(f"{instruction}\t{address} {operation.name.lower()} x{rs1}, x{rs2}, #{immediate}")

                    elif instruction[30:32] == InstructionCategory.CATEGORY_2.value:
                        opcode = instruction[25:30]
                        rd = int(instruction[20:25], 2)
                        rs1 = int(instruction[12:17], 2)
                        rs2 = int(instruction[7:12], 2)
                        func3 = "000"
                        func7 = "0000000"

                        operation = Category2Opcode(opcode)
                        disassebly_output.append(f"{instruction}\t{address} {operation.name.lower()} x{rd}, x{rs1}, x{rs2}")

                    elif instruction[30:32] == InstructionCategory.CATEGORY_3.value:
                        opcode = instruction[25:30]
                        rd = int(instruction[20:25], 2)
                        rs1 = int(instruction[12:17], 2)
                        immediate = instruction[0:12]
                        immediate = twos_complement(immediate)
                        func3 = "000"

                        operation = Category3Opcode(opcode)
                        if operation == Category3Opcode.LW:
                            disassebly_output.append(f"{instruction}\t{address} {operation.name.lower()} x{rd}, {immediate}(x{rs1})")
                        else:
                            disassebly_output.append(f"{instruction}\t{address} {operation.name.lower()} x{rd}, x{rs1}, #{immediate}")

                    elif instruction[30:32] == InstructionCategory.CATEGORY_4.value:
                        opcode = instruction[25:30]
                        if opcode == Category4Opcode.BREAK.value:
                            disassebly_output.append(f"{instruction}\t{address} break")
                            self.state = DissasemblyState.DATA
                        elif opcode == Category4Opcode.JAL.value:
                            rd = int(instruction[20:25], 2)
                            immediate = instruction[0:20]
                            immediate = twos_complement(immediate)
                            disassebly_output.append(f"{instruction}\t{address} jal x{rd}, #{immediate}")

                elif self.state == DissasemblyState.DATA:
                    data_value = twos_complement(instruction)
                    self.memory[address] = data_value
                    disassebly_output.append(f"{instruction}\t{address} {data_value}")

                address += 4

        with open("disassembly.txt", 'w') as outfile:
            for line in disassebly_output:
                outfile.write(line + "\n")


class Processor():

    def __init__(self):
        pass

    def process(self):
        pass



def main():
    parser = argparse.ArgumentParser(description="RISC-V Simulator")
    parser.add_argument("riscv_text", type=str, help="Path to the input file containing assembly instructions")
    
    args = parser.parse_args()
    riscv_text = args.riscv_text

    disassembler = Disassembler(riscv_text=riscv_text)
    disassembler.disassemble(riscv_text=riscv_text)

    processor = Processor()
    processor.process()



if __name__ == "__main__":
    main()