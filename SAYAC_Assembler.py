import sys

# constants
VERSION = "v1.0.0-alpha01"
INSTRUCTIONS = [
    "ldr",  # LdR -> load from memory or I/O peripheral
    "str",  # STR -> Store to memory or I/O peripheral
    "jmr",  # JMR -> Jump to address
    "jmi",  # JMI -> Jump to immediate address
    "anr",  # ANR -> Logical AND operation
    "ani",  # ANI -> Logical AND operation with immediate value
    "msi",  # MSI -> Move low sign extended immediate to register
    "mhi",  # MHI -> Move high immediate to register
    "slr",  # SLR -> Logical Left/Right shift
    "sar",  # SAR -> Arithmetic Left/Right shift
    "add",  # ADD -> Adding two registers
    "sub",  # SUB -> Subtracting two registers
    "adi",  # ADI -> Adding Immediate to register
    "sui",  # SUI -> Subtracting Immediate from register
    "mul",  # MUL -> Multiplying two registers
    "div",  # DIV -> Dividing two registers
    "cmr",  # CMR -> Comparing two registers
    "cmi",  # CMI -> Comparing register and Immediate value
    "brc",  # BRC -> Branch Registered with Condition
    "brr",  # BRR -> Branch Registered Relative with Condition
    "sar",  # SAR -> Arithmetic Logical shift with immediate
    "ntr",  # NTR -> Logical NOT
    "ntd",  # NTD -> Logical NOT
]

# App info
print(f"SAYAC Assembler {VERSION}")

if len(sys.argv) < 2:
    print("Error: Not enough arguments --> [file name not found]")
    exit(1)

# get file name from terminal
insFileName = sys.argv[1]

try:
    # open the SAYAC Assembly code from the path given
    insFile = open(insFileName, "r")

    insFile.close()
    pass
except FileNotFoundError:
    print(f"Error: File not found --> ['{insFileName}' does not exists]")
    pass
