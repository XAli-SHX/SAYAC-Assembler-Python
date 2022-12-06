import sys

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


# Exceptions
class AssemblySyntaxError(Exception):
    def __init__(self, message):
        self.message = message


# App info
print(f"SAYAC Assembler {VERSION}")

if len(sys.argv) < 2:
    print("Error: Not enough arguments --> [file name not found]")
    exit(1)

# get file name from terminal
insFileName = sys.argv[1]
binFileLines = []


def hexToInt(num: str):
    if num.__contains__("0x"):
        return int(num, 0)
    return int(num, 16)


def intToBin(num: str, n: int):
    return bin(int(num)).replace("0b", "")[-n:]


def parseInstruction(ins, line):
    insSplitted = ins.strip().split(" ")
    if len(insSplitted) < 1:
        raise AssemblySyntaxError(f"No instruction on line {line}")
    insType = insSplitted[0].lower()
    if INS_REQUIRED_ARGS_COUNT[insType] != (len(insSplitted) - 1):
        raise AssemblySyntaxError(f"Not enough argument for instruction '{insType}'")
    if insType == INS_LdR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_00_0_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_LdRio:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_00_1_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_STR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_01_0_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
        pass
    elif insType == INS_STRio:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_01_1_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
        pass
    elif insType == INS_JMR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_10_0_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
        pass
    elif insType == INS_JMRs:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"0010_10_1_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_JMI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"0010_11_{intToBin(imm, 6)}_{intToBin(rd, 4)}")
    elif insType == INS_ANR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"0011_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_ANI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"0100_{intToBin(imm, 8)}_{intToBin(rd, 4)}")
    elif insType == INS_MSI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"0101_{intToBin(imm, 8)}_{intToBin(rd, 4)}")
    elif insType == INS_MHI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"0110_{intToBin(imm, 8)}_{intToBin(rd, 4)}")
    elif insType == INS_SLR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"0111_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_SAR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1000_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_ADD:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1001_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_ADR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1001_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_SUB:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1010_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_SUR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1010_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_ADI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"1011_{intToBin(imm, 8)}_{intToBin(rd, 4)}")
    elif insType == INS_SUI:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        imm = insSplitted[2]
        binFileLines.append(f"1100_{intToBin(imm, 8)}_{intToBin(rd, 4)}")
    elif insType == INS_MUL:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1101_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_DIV:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        rs2 = insSplitted[3].replace("_", "").replace("r", "")
        binFileLines.append(f"1110_{intToBin(rs1, 4)}_{intToBin(rs2, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_CMR:
        rs1 = insSplitted[1].replace("_", "").replace("r", "")
        rs2 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_000_0_{intToBin(rs2, 4)}_{intToBin(rs1, 4)}")
    elif insType == INS_CMI:
        imm = insSplitted[1]
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_001_{intToBin(imm, 5)}_{intToBin(rs1, 4)}")
    elif insType == INS_BRC:
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_010_{intToBin(str(hexToInt(FIB)), 5)}_{intToBin(rd, 4)}")
    elif insType == INS_BRR:
        FIB = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_011_{intToBin(str(hexToInt(FIB)), 5)}_{intToBin(rd, 4)}")
    elif insType == INS_SHI:
        shimm = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_10_0_{intToBin(shimm, 5)}_{intToBin(rd, 4)}")
    elif insType == INS_SHIla:
        shimm = insSplitted[1]
        rd = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_10_1_{intToBin(shimm, 5)}_{intToBin(rd, 4)}")
    elif insType == INS_NTR:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_110_0_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_NTR2c:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        rs1 = insSplitted[2].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_110_1_{intToBin(rs1, 4)}_{intToBin(rd, 4)}")
    elif insType == INS_NTD:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_111_0_0000_{intToBin(rd, 4)}")
    elif insType == INS_NTD2c:
        rd = insSplitted[1].replace("_", "").replace("r", "")
        binFileLines.append(f"1111_111_1_0000_{intToBin(rd, 4)}")
    else:
        raise Exception("Uncaught!")


try:
    # open the SAYAC Assembly code from the path given
    insFile = open(insFileName, "r")
    insLines = insFile.readlines()
    insFile.close()
    for lineIndex in range(0, len(insLines)):
        parseInstruction(insLines[lineIndex], lineIndex + 1)
    binFileName = insFileName.rsplit(".", maxsplit=1)[0]
    binFile = open(binFileName + ".bin", "w")
    binFile.write("\n")
    for lineIndex in range(0, len(insLines)):
        binFile.write(f"{binFileLines[lineIndex]}\n")
    binFile.close()
    print("Successfully Assembled!")
except FileNotFoundError:
    print(f"Error: File not found --> ['{insFileName}' does not exists]")
except KeyError as e:
    print(f"Error: Instruction {e} not supported yet")
except AssemblySyntaxError as e:
    print(f"Error: {e.message}")
except Exception as e:
    print(f"Error: Unhandled exception --> [{e}]")
