import sys
import os
import json
import re

# constants
VERSION = "v1.0.0-alpha03"

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


def commentRemover(lines: list):
    text = ""
    for line in lines:
        text += line + ";"

    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "  # note: a space and not an empty string
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    newText = re.sub(pattern, replacer, text)
    newList = newText.split(";")
    newList = [line.strip() for line in newList if line.strip() != ""]
    return newList


class Sayac:
    def __init__(self):
        self.registers: list = [i for i in range(0, 16)]
        self.memory = {}
        self.memoryIO = {}
        # Flags
        self.FLAG_GT: bool = False
        self.FLAG_GT_EQ: bool = False
        self.FLAG_EQ: bool = False
        self.FLAG_NEQ: bool = True
        self.FLAG_LT: bool = False
        self.FLAG_LT_EQ: bool = False
        self.PC: int = 0

    def createAssemblerOutJsonFile(self, name: str):
        f = open(f"{name}.sayac.json", "w")
        content = {
            "PC": self.PC,
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

    def setFlags(self, val1: int, val2: int):
        self.FLAG_GT = False
        self.FLAG_GT_EQ = False
        self.FLAG_EQ = False
        self.FLAG_NEQ = True
        self.FLAG_LT = False
        self.FLAG_LT_EQ = False
        if val1 == val2:
            self.FLAG_EQ = True
            self.FLAG_NEQ = False
            self.FLAG_LT_EQ = True
            self.FLAG_GT_EQ = True
        if val1 > val2:
            self.FLAG_GT = True
        if val1 < val2:
            self.FLAG_LT = True


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


def extractInt(cmd: str, excludeLetter: str):
    cmd = cmd.replace(excludeLetter, "")
    return baseNumberToInt(cmd)


def exeRegisterCommand(sayac: Sayac, cmd: str):
    try:
        if cmd == "r":
            print(sayac.registers)
        else:
            print(f"{cmd} = {sayac.registers[extractInt(cmd, 'r')]}")
    except ValueError:
        print(f"Error: {extractInt(cmd, 'r')} is an invalid number")


def exeMemoryCommand(sayac: Sayac, cmd: str):
    try:
        if cmd == "m":
            print(sayac.memory)
        else:
            print(f"{cmd} = {sayac.readMemory(extractInt(cmd, 'm'))}")
    except ValueError:
        print(f"Error: {extractInt(cmd, 'r')} is an invalid number")


def exeFlagCommand(sayac: Sayac):
    print(f"GT: {sayac.FLAG_GT}")
    print(f"GT_EQ: {sayac.FLAG_GT_EQ}")
    print(f"EQ: {sayac.FLAG_EQ}")
    print(f"NEQ: {sayac.FLAG_NEQ}")
    print(f"LT: {sayac.FLAG_LT}")
    print(f"LT_EQ: {sayac.FLAG_LT_EQ}")


def getInput(sayac: Sayac):
    try:
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
    except Exception as e:
        print(f"Invalid command: {e}")
        getInput(sayac)


# Exceptions
class AssemblySyntaxError(Exception):
    def __init__(self, message):
        self.message = message


def hexToInt(num: str):
    if num.startswith("0x"):
        return int(num, 0)
    return int(num, 16)


def intToBin(num: int, n: int):
    binNum = bin(int(num)).replace("0b", "")[-n:]
    while len(binNum) < n:
        binNum = "0" + binNum
    if len(binNum) > n:
        return binNum[-n:]
    return binNum


def baseNumberToInt(num: str):
    if num.startswith("0x"):
        return hexToInt(num)
    elif num.startswith("0b"):
        return int(num, 2)
    return int(num)


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
        sayac.PC += sayac.registers[int(rs1)] - 1
    elif insType == INS_JMRs:
        # JMRs rd rs1
        # PC <- PC + rs1
        # rd <- PC + 1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.PC + 1
        sayac.PC += sayac.registers[int(rs1)] - 1
    elif insType == INS_JMI:
        # JMI rd imm
        # PC <- PC + imm
        # rd <- PC + 1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = sayac.PC + 1
        sayac.PC += baseNumberToInt(imm) - 1
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
        sayac.registers[int(rd)] = sayac.registers[int(rd)] & baseNumberToInt(imm)
    elif insType == INS_MSI:
        # MSI rd imm
        # rd[7:0] <- SE(imm)
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = baseNumberToInt(imm)
    elif insType == INS_MHI:
        # TODO: check the operation
        # MHI rd imm
        # rd[15:8] <- imm
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = baseNumberToInt(imm) << 8
    elif insType == INS_SLR:
        # SLR rd rs1 rs2
        # rd <- rs1 << (+- rs2[4:0])
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        rs2_4to0 = intToBin(sayac.registers[int(rs2)], 5)
        if rs2_4to0[0] == "0":
            sayac.registers[int(rd)] = abs(sayac.registers[int(rs1)]) >> int(rs2_4to0, 2)
        else:
            sayac.registers[int(rd)] = abs(sayac.registers[int(rs1)]) << int(rs2_4to0[1:], 2)
    elif insType == INS_SAR:
        # SAR rd rs1 rs2
        # rd <- rs1 <<< (+- rs2[4:0])
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        rs2_4to0 = intToBin(sayac.registers[int(rs2)], 5)
        if rs2_4to0[0] == "0":
            sayac.registers[int(rd)] = sayac.registers[int(rs1)] >> int(rs2_4to0, 2)
        else:
            sayac.registers[int(rd)] = sayac.registers[int(rs1)] << int(rs2_4to0[1:], 2)
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
        # ADI rd imm
        # rd <- rd + imm
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = sayac.registers[int(rd)] + baseNumberToInt(imm)
    elif insType == INS_SUI:
        # SUI rd imm
        # rd <- rd - imm
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        sayac.registers[int(rd)] = sayac.registers[int(rd)] - baseNumberToInt(imm)
    elif insType == INS_MUL:
        # MUL rd rs1 rs2
        # rd <- rs1 * rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = sayac.registers[int(rs1)] * sayac.registers[int(rs2)]
    elif insType == INS_DIV:
        # DIV rd rs1 rs2
        # rd <- rs1 / rs2
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = int(sayac.registers[int(rs1)] / sayac.registers[int(rs2)])
    elif insType == INS_CMR:
        # CMR rs1 rs2
        rs1 = insSplitted[1].replace("_", "").replace("r", "")
        rs2 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.setFlags(sayac.registers[int(rs1)], sayac.registers[int(rs2)])
    elif insType == INS_CMI:
        # CMI rs1 imm
        imm = insSplitted[1]
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.setFlags(sayac.registers[int(rs1)], baseNumberToInt(imm))
    elif insType == INS_BRC:
        # BRC cond rd
        # if (cond) pc <- rd
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        if sayac.FIBtoFlag(intToBin(baseNumberToInt(FIB), 5)):
            sayac.PC = sayac.registers[int(rd)] - 1
    elif insType == INS_BRR:
        # BRR cond rd
        # if (cond) pc <- pc + rd
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        if sayac.FIBtoFlag(intToBin(baseNumberToInt(FIB), 5)):
            sayac.PC += sayac.registers[int(rd)] - 1
    elif insType == INS_SHI:
        # SHI imm rd
        # rd <- rd << (+- imm)
        shimm = baseNumberToInt(insSplitted[1])
        rd = insSplitted[2].replace("_", "").replace("r", "")
        if int(shimm) < 0:
            sayac.registers[int(rd)] = abs(sayac.registers[int(rd)]) << int(abs(shimm))
        else:
            sayac.registers[int(rd)] = abs(sayac.registers[int(rd)]) >> int(shimm)
    elif insType == INS_SHIla:
        # SHIla imm rd
        # rd <- rd <<< (+- imm)
        shimm = baseNumberToInt(insSplitted[1])
        rd = insSplitted[2].replace("_", "").replace("r", "")
        if int(shimm) < 0:
            sayac.registers[int(rd)] = sayac.registers[int(rd)] << int(abs(shimm))
        else:
            sayac.registers[int(rd)] = sayac.registers[int(rd)] >> int(shimm)
    elif insType == INS_NTR:
        # NTR rd rs1
        # rd <- ~rs1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = ~sayac.registers[int(rs1)]
    elif insType == INS_NTR2c:
        # NTR2c rd rs1
        # rd <- ~rs1 + 1
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = ~sayac.registers[int(rs1)] + 1
    elif insType == INS_NTD:
        # NTD rd
        rd = insSplitted[1].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = ~sayac.registers[int(rd)]
    elif insType == INS_NTD2c:
        # NTD2c rd
        rd = insSplitted[1].replace("_", "").replace("r", "")
        sayac.registers[int(rd)] = ~sayac.registers[int(rd)] + 1
    else:
        raise Exception("Uncaught!")


def assemble(insFileName, lineByLine: bool):
    try:
        sayac = Sayac()
        # open the SAYAC Assembly code from the path given
        insFile = open(insFileName, "r")
        insLines = insFile.readlines()
        insFile.close()
        insLines = commentRemover(insLines)
        while sayac.PC in range(0, len(insLines)):
            lineIndex = sayac.PC
            parseInstruction(insLines[lineIndex], lineIndex + 1, sayac)
            sayac.createAssemblerOutJsonFile(insFileName.rsplit(".", 1)[0])
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
