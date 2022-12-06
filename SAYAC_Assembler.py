import sys

VERSION = "v1.0.0"
print(f"SAYAC Assembler {VERSION}")
if len(sys.argv) < 2:
    print("Error: Not enough arguments --> [file name not found]")
    exit(1)

insFileName = sys.argv[1]
print(insFileName)

