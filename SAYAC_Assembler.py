import sys
import os
import json

# constants
VERSION = "v1.0.0-alpha01"

INS_LdR = "ldr"  # load from memory
INS_LdRio = "ldrio"  # load from I/O peripheral
INS_STR = "str"  # Store to memory
INS_STRio = "strio"  # Store to I/O peripheral
INS_JMR = "jmr"  # Jump to address
INS_JMRs = "jmrs"  # Jump to address & save PC
INS_JMI = "jmi"  # Jump to immediate address
INS_ANR = "anr"  # Logical AND operation
INS_AND = "and"  # Logical AND operation # TODO: remove this line (instruction is not in the ISR)
INS_ANI = "ani"  # Logical AND operation with immediate value
INS_MSI = "msi"  # Move low sign extended immediate to register
INS_MHI = "mhi"  # Move high immediate to register
INS_SLR = "slr"  # Logical Left/Right shift
INS_SAR = "sar"  # Arithmetic Left/Right shift
INS_ADD = "add"  # Adding two registers
INS_ADR = "adr"  # Adding two registers
INS_SUB = "sub"  # Subtracting two registers
INS_SUR = "sur"  # Subtracting two registers
INS_ADI = "adi"  # Adding Immediate to register
INS_SUI = "sui"  # Subtracting Immediate from register
INS_MUL = "mul"  # Multiplying two registers
INS_DIV = "div"  # Dividing two registers
INS_CMR = "cmr"  # Comparing two registers
INS_CMI = "cmi"  # Comparing register and Immediate value
INS_BRC = "brc"  # Branch Registered with Condition
INS_BRR = "brr"  # Branch Registered Relative with Condition
INS_SHI = "shi"  # Arithmetic Logical shift with immediate
INS_SHIla = "shila"  # Arithmetic Logical shift with immediate
INS_NTR = "ntr"  # Logical NOT
INS_NTR2c = "ntr2c"  # Logical NOT 2's complement
INS_NTD = "ntd"  # Logical NOT
INS_NTD2c = "ntd2c"  # Logical NOT 2's complement

INS_REQUIRED_ARGS_COUNT = {
    INS_LdR: 2,
    INS_LdRio: 2,
    INS_STR: 2,
    INS_STRio: 2,
    INS_JMR: 2,
    INS_JMRs: 2,
    INS_JMI: 2,
    INS_ANR: 3,
    INS_AND: 3,
    INS_ANI: 2,
    INS_MSI: 2,
    INS_MHI: 2,
    INS_SLR: 3,
    INS_SAR: 3,
    INS_ADD: 3,
    INS_ADR: 3,
    INS_SUB: 3,
    INS_SUR: 3,
    INS_ADI: 2,
    INS_SUI: 2,
    INS_MUL: 3,
    INS_DIV: 3,
    INS_CMR: 2,
    INS_CMI: 2,
    INS_BRC: 2,
    INS_BRR: 2,
    INS_SHI: 2,
    INS_SHIla: 2,
    INS_NTR: 2,
    INS_NTR2c: 2,
    INS_NTD: 1,
    INS_NTD2c: 1,
}


class Sayac:
    def __init__(self):
        self.registers = [i for i in range(0, 16)]
        self.memory = {}
        self.memoryIO = {}
        # Flags
        self.FLAG_GT = False
        self.FLAG_GT_EQ = False
        self.FLAG_EQ = False
        self.FLAG_NEQ = False
        self.FLAG_LT = False
        self.FLAG_LT_EQ = False
        self.PC = 0

    def createAssemblerOutJsonFile(self, name: str):
        f = open(f"{name}.sayac.json", "w")
        content = {
            "registers": self.registers,
            "memory": self.memory,
            "memoryIO": self.memoryIO,
            "flags": {
                "gt": self.FLAG_GT,
                "gt_eq": self.FLAG_GT_EQ,
                "eq": self.FLAG_EQ,
                "neq": self.FLAG_NEQ,
                "lt": self.FLAG_LT,
                "lt_eq": self.FLAG_LT_EQ,
            }
        }
        f.write(json.dumps(content))
        f.close()

    def FIBtoFlag(self, fib5bit: str):
        if len(fib5bit) != 5:
            raise Exception("FIB must be 5 bit")
        fib = fib5bit[2:]
        if fib == "000":
            return self.FLAG_EQ
        elif fib == "001":
            return self.FLAG_LT
        elif fib == "010":
            return self.FLAG_GT
        elif fib == "011":
            return self.FLAG_GT_EQ
        elif fib == "100":
            return self.FLAG_LT_EQ
        elif fib == "101":
            return self.FLAG_NEQ
        else:
            raise Exception("Invalid FIB")

    def readMemory(self, address: int, fromIO: bool = False):
        memory = self.memoryIO if fromIO else self.memory
        if address in memory:
            return memory[address]
        return address

    def writeMemory(self, address: int, value: int, fromIO: bool = False):
        memory = self.memoryIO if fromIO else self.memory
        memory[address] = value


def main():
    # App info
    print(f"SAYAC Assembler {VERSION}")

    if len(sys.argv) < 2:
        print("Error: Not enough arguments --> [file name not found]")
        exit(1)

    # get file name from terminal
    insFileName = sys.argv[1]
    lineByLine = False
    if len(sys.argv) > 2:
        if sys.argv[2] == "--line":
            lineByLine = True
    assemble(insFileName, lineByLine)


def extractNumber(cmd: str, excludeLetter: str):
    cmd = cmd.replace(excludeLetter, "")
    return int(cmd)


def exeRegisterCommand(sayac: Sayac, cmd: str):
    try:
        if cmd == "r":
            print(sayac.registers)
        else:
            print(f"{cmd} = {sayac.registers[extractNumber(cmd, 'r')]}")
    except ValueError:
        print(f"Error: {extractNumber(cmd, 'r')} is an invalid number")


def exeMemoryCommand(sayac: Sayac, cmd: str):
    try:
        if cmd == "m":
            print(sayac.memory)
        else:
            if cmd.replace("m", "").startswith("0x"):
                print(f"{cmd} = {sayac.readMemory(hexToInt(cmd.replace('m', '')))}")
            else:
                print(f"{cmd} = {sayac.readMemory(extractNumber(cmd, 'm'))}")
    except ValueError:
        print(f"Error: {extractNumber(cmd, 'r')} is an invalid number")


def exeFlagCommand(sayac: Sayac):
    print(f"GT: {sayac.FLAG_GT}")
    print(f"GT_EQ: {sayac.FLAG_GT_EQ}")
    print(f"EQ: {sayac.FLAG_EQ}")
    print(f"NEQ: {sayac.FLAG_NEQ}")
    print(f"LT: {sayac.FLAG_LT}")
    print(f"LT_EQ: {sayac.FLAG_LT_EQ}")


def getInput(sayac: Sayac):
    print("sayac>>> ", end="")
    cmd = input().strip()
    if cmd == "":
        return
    elif cmd.startswith("r"):
        exeRegisterCommand(sayac, cmd)
    elif cmd.startswith("m"):
        exeMemoryCommand(sayac, cmd)
    elif cmd == "f":
        exeFlagCommand(sayac)
    elif cmd == "a":
        print("Registers:")
        exeRegisterCommand(sayac, "r")
        print("Memory:")
        exeMemoryCommand(sayac, "m")
        print("Flags:")
        exeFlagCommand(sayac)
    else:
        print("Invalid command")
    getInput(sayac)


# Exceptions
class AssemblySyntaxError(Exception):
    def __init__(self, message):
        self.message = message


def hexToInt(num: str):
    if num.startswith("0x"):
        return int(num, 0)
    return int(num, 16)


def intToBin(num: str, n: int):
    binNum = bin(int(num)).replace("0b", "")[-n:]
    while len(binNum) < n:
        binNum = "0" + binNum
    return binNum


def parseInstruction(ins, line, sayac: Sayac):
    insSplitted = ins.strip().split(" ")
    if len(insSplitted) < 1:
        raise AssemblySyntaxError(f"No instruction on line {line}")
    insType = insSplitted[0].lower()
    if INS_REQUIRED_ARGS_COUNT[insType] != (len(insSplitted) - 1):
        raise AssemblySyntaxError(f"Not enough argument for instruction '{insType}'")
    if insType == INS_LdR:
        # LdR rd rs1
        # rd <- mem[rs1]
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.readMemory(sayac.registers[int(rs1)])
    elif insType == INS_LdRio:
        # LdRio rd rs1
        # rd <- memio[rs1]
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.readMemory(sayac.registers[int(rs1)], True)
    elif insType == INS_STR:
        # STR rd rs1
        # mem[rd] <- rs1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.writeMemory(sayac.registers[int(rd)], sayac.registers[int(rs1)])
    elif insType == INS_STRio:
        # STRio rd rs1
        # memio[rd] <- rs1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.writeMemory(sayac.registers[int(rd)], sayac.registers[int(rs1)], True)
    elif insType == INS_JMR:
        # JMR rd rs1
        # PC <- PC + rs1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.PC += sayac.registers[int(rs1)]
        pass
    elif insType == INS_JMRs:
        # JMRs rd rs1
        # PC <- PC + rs1
        # rd <- PC + 1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.PC + 1
        sayac.PC += sayac.registers[int(rs1)]
    elif insType == INS_JMI:
        # JMI rd imm
        # PC <- PC + imm
        # rd <- PC + 1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = sayac.PC + 1
        sayac.PC += int(imm)
    elif insType == INS_ANR:
        # ANR rd rs1 rs2
        # rd <- rs1 & rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] & sayac.registers[int(rs2)]
    elif insType == INS_AND:
        # ANR rd rs1 rs2
        # rd <- rs1 & rs2
        # TODO: remove this instruction
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] & sayac.registers[int(rs2)]
    elif insType == INS_ANI:
        # ANI rd imm
        # rd <- rd & imm
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = sayac.registers[int(rd)] & int(imm)
    elif insType == INS_MSI:
        # MSI rd imm
        # rd[7:0] <- SE(imm)
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = imm
    elif insType == INS_MHI:
        # MHI rd imm
        # rd[15:8] <- imm
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = imm << 8
    elif insType == INS_SLR:
        # SLR rd rs1 rs2
        # rd <- rs1 << (+- rs2[4:0])
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        rs2_4to0 = intToBin(str(sayac.registers[int(rs2)]), 5)
        if rs2_4to0[0] == "0":
            sayac.registers[int(rd)] = sayac.registers[int(rs1)] >> int(rs2_4to0, 2)
        else:
            # TODO: see how to deal with rs2_4to0 (sign & mag OR two's comp.)
            sayac.registers[int(rd)] = sayac.registers[int(rs1)] >> int(rs2_4to0, 2)
    elif insType == INS_SAR:
        # SAR rd rs1 rs2
        # rd <- rs1 <<< (+- rs2[4:0])
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        rs2_4to0 = intToBin(str(sayac.registers[int(rs2)]), 5)
        rs1_sign = intToBin(str(sayac.registers[int(rs1)]), 16)[0]
        if rs2_4to0[0] == "0":
            shv = int(rs2_4to0, 2)
            if rs1_sign == "0":
                sayac.registers[int(rd)] = sayac.registers[int(rs1)] >> shv
            else:
                sayac.registers[int(rd)] = int("1" * shv + str(sayac.registers[int(rs1)] >> shv))
        else:
            # TODO: see how to deal with rs2_4to0 (sign & mag OR two's comp.)
            sayac.registers[int(rd)] = sayac.registers[int(rs1)] >> int(rs2_4to0, 2)
    elif insType == INS_ADD:
        # ADD rd rs1 rs2
        # rd <- rs1 + rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] + sayac.registers[int(rs2)]
    elif insType == INS_ADR:
        # ADR rd rs1 rs2
        # rd <- rs1 + rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] + sayac.registers[int(rs2)]
    elif insType == INS_SUB:
        # SUB rd rs1 rs2
        # rd <- rs1 - rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] - sayac.registers[int(rs2)]
    elif insType == INS_SUR:
        # SUR rd rs1 rs2
        # rd <- rs1 - rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] - sayac.registers[int(rs2)]
    elif insType == INS_ADI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        return f"1011_{intToBin(imm, 8)}_{intToBin(rd, 4)}"
    elif insType == INS_SUI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        return f"1100_{intToBin(imm, 8)}_{intToBin(rd, 4)}"
    elif insType == INS_MUL:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        return f"1101_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}"
    elif insType == INS_DIV:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        return f"1110_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}"
    elif insType == INS_CMR:
        rs1 = insSplitted[1].replace("_", "").replace("r", "")
        rs2 = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_000_0_{intToBin(rs2, 4)}_{intToBin(rs1, 4)}"
    elif insType == INS_CMI:
        imm = insSplitted[1]
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_001_{intToBin(imm, 5)}_{intToBin(rs1, 4)}"
    elif insType == INS_BRC:
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_010_{intToBin(str(hexToInt(FIB)), 5)}_{intToBin(rd, 4)}"
    elif insType == INS_BRR:
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_011_{intToBin(str(hexToInt(FIB)), 5)}_{intToBin(rd, 4)}"
    elif insType == INS_SHI:
        shimm = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_10_0_{intToBin(shimm, 5)}_{intToBin(rd, 4)}"
    elif insType == INS_SHIla:
        shimm = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_10_1_{intToBin(shimm, 5)}_{intToBin(rd, 4)}"
    elif insType == INS_NTR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_110_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}"
    elif insType == INS_NTR2c:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        return f"1111_110_1_{intToBin(rs1, 4)}_{intToBin(rd, 4)}"
    elif insType == INS_NTD:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        return f"1111_111_0_0000_{intToBin(rd, 4)}"
    elif insType == INS_NTD2c:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        return f"1111_111_1_0000_{intToBin(rd, 4)}"
    else:
        raise Exception("Uncaught!")


def assemble(insFileName, lineByLine: bool):
    try:
        sayac = Sayac()
        # open the SAYAC Assembly code from the path given
        insFile = open(insFileName, "r")
        insLines = insFile.readlines()
        insFile.close()
        while sayac.PC in range(0, len(insLines)):
            lineIndex = sayac.PC
            parseInstruction(insLines[lineIndex], lineIndex + 1, sayac)
            if lineByLine:
                print(insLines[lineIndex])
                getInput(sayac)
            sayac.PC += 1
        print("Successfully Assembled!")
        getInput(sayac)
    except FileNotFoundError:
        print(f"Error: File not found --> ['{insFileName}' does not exists]")
    except KeyError as e:
        print(f"Error: Instruction {e} not supported yet")
    except AssemblySyntaxError as e:
        print(f"Error: {e.message}")
    except Exception as e:
        print(f"Error: Unhandled exception --> [{e}]")


if __name__ == "__main__":
    main()
