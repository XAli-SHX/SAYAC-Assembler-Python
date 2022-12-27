# SAYAC Assembler Python

This project is a one-file python code to get input from the command line and turn that into binary code with the exact
same name as the input.

## How To Use It

### Instruction to Binary

- To convert a single file:

```
python SAYAC_Inst2Bin.py "SAYAC instruction file path"
```

- To convert all files in the directory with file-type filter:

```
python SAYAC_Inst2Bin.py --all=txt
```

### Assembler

- all-at-once

To assemble all lines of a file

```
python SAYAC_Assembler.py <filename>
```

- line-by-line

To assemble a file line by line

```
python SAYAC_Assembler.py <filename> --line
```

#### Commands

After assembling the file, you can use the following commands (in both line-by-line and all-at-once modes):

- ` `[blank line] run next line (finish the program in all-at-once mode)
- `r<x>` get the value of register x (e.g. r1)
- `m<x>` get the value of memory at the address x (e.g. m1000 or m0x3e8)
- `r` print all the registers and their values
- `m` print all the changed memory and their values
- `f` print all the flags and their values
- `a` print all the registers, changed memory addresses and flags

Notice that the assembler will keep getting input until user gives blank line as input.

## Info

- python version: 3.8