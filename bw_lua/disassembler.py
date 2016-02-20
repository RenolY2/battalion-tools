import struct

INSTRUCTIONS = {
     0: "MOVE       {A} {B}",
     1: "LOADK      {A} {Bx}",
     2: "LOADBOOL   {A} {B} {C}",
     3: "LOADNIL    {A} {B}",
     4: "GETUPVAL   {A} {B}",
     5: "GETGLOBAL  {A} {Bx}",
     6: "GETTABLE   {A} {B} {C}",
     7: "SETGLOBAL  {A} {Bx}",
     8: "SETUPVAL   {A} {B}",
     9: "SETTABLE   {A} {B} {C}",
    10: "NEWTABLE   {A} {B} {C}",
    11: "SELF       {A} {B} {C}",
    12: "ADD        {A} {B} {C}",
    13: "SUB        {A} {B} {C}",
    14: "MUL        {A} {B} {C}",
    15: "DIV        {A} {B} {C}",
    16: "POW        {A} {B} {C}",
    17: "UNM        {A} {B}",
    18: "NOT        {A} {B}",
    19: "CONCAT     {A} {B} {C}",
    20: "JMP        {sBx}",
    21: "EQ         {A} {B} {C}",
    22: "LT         {A} {B} {C}",
    23: "LE         {A} {B} {C}",
    24: "TEST       {A} {B} {C}",
    25: "CALL       {A} {B} {C}",
    26: "TAILCALL   {A} {B} {C}",
    27: "RETURN     {A} {B}",
    28: "FORLOOP    {A} {sBx}",
    29: "TFORLOOP   {A} {C}",
    30: "TFORPREP   {A} {sBx}",
    31: "SETLIST    {A} {Bx}",
    32: "SETLISTO   {A} {Bx}",
    33: "CLOSE      {A}",
    34: "CLOSURE    {A} {Bx}"

}

def parse(code):
    #num1, num2, num3, num4 = struct.unpack("BBBB", code)
    num = struct.unpack("I", code)[0]
    #print(bin(num))
    #"""
    opcode = num & 0b111111
    C = (num >> 6) & 0x1FF
    B = (num >> (6+9)) & 0x1FF
    A = (num >> (6+9+9)) & 0xFF
    """A = (num >> 6) & 0xFF

    B = (num >> (6+8)) & 0x1FF

    C = (num >> (6+8+9)) & 0x1FF
    """
    """
    C = num & 0x1FF
    B = (num >> 9) & 0x1FF
    A = (num >> (9+9)) & 0xFF
    opcode = num >> (9+9+8)
    """

    return opcode, A, B, C


if __name__ == "__main__":
    input_name = "lua_compiled.bin"

    with open(input_name, "rb") as f:
        data = f.read()

    for i in range(4, len(data), 4):
        parsed = parse(data[i:i+4])

        opcode = parsed[0]
        #print(parsed)
        print(INSTRUCTIONS[opcode], parsed)

