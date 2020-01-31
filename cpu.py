"""CPU functionality."""

import sys

alu_dict = {
    0b10100000: 'ADD',
    0b10100001: 'SUB',
    0b10100010: 'MUL',
    0b10100011: 'DIV',
    0b10100100: 'MOD'
}

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # Allocates 256 bytes of memory
        self.reg = [0] * 8 # Register
        self.pc = 0 # Program counter; points to the current instruction
        self.sp = 7 # Stack pointer; lives in register spot 7

        ########## INSTRUCTION HANDLERS ##########
        self.LDI  = 0b10000010
        self.PRN  = 0b01000111
        self.HLT  = 0b00000001
        self.PUSH = 0b01000101
        self.POP  = 0b01000110
        self.CALL = 0b01010000
        self.RET  = 0b00010001

    def load(self):
        """Load a program into memory."""
        # Check to see if there are two arguments
        # Second argument must be the filename of program to load
        if len(sys.argv) != 2:
            print('Usage: file.py <filename>', file=sys.stderr)
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    # Ignore comments
                    comment_split = line.split('#')
                    num = comment_split[0].strip()
                    
                    if num == '':
                        # Ignore blank lines
                        continue
                    
                    value = int(num, 2)
                    self.ram[address] = value
                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} not found.')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            # Add the value in two registers and store the result in registerA
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            # Subtract the value in the second register from the first, storing
            # the result in registerA
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            # Multiply the values in two registers together and store the
            # result in registerA
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            # Divide the value in the first register by the value in the second,
            # storing the result in registerA
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == 'MOD':
            # Divide the value in the first register by the value in the second,
            # storing the remainder of the result in registerA
            # If the value in the second register is 0, the system should print
            # an error message and halt.
            if reg_b is not 0:
                self.reg[reg_a] %= self.reg[reg_b]
            else:
                sys.exit('Second value can not be zero.')
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # Memory Address Register: address that is being read/written to
    def ram_read(self, MAR):
        return self.ram[MAR]

    # Memory Data Register: data that was read/data to write
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    # Set the value of a register to an integer.

    def run(self):
        """Run the CPU."""
        while True:
            # Instruction Register (IR)
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            if IR is self.LDI:
                # Insert a decimal integer into a register
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif IR is self.PRN:
                # Print to the console the decimal integer value that is
                # stored in the given register.
                print(self.reg[operand_a])
                self.pc += 2
            elif IR is self.PUSH:
                """
                Push the value in the given register on the stack.
                    1. Decrement the SP.
                    2. Copy the value in the given register to the address
                    pointed to by SP.
                """
                self.sp -= 1
                self.ram[self.sp] = self.reg[operand_a]
                self.pc += 2
            elif IR is self.POP:
                """
                Pop the value at the top of stack into the given register.
                    1. Copy the value from the address pointed to by SP to
                    the given register.
                    2. Increment SP.
                """
                self.reg[operand_a] = self.ram[self.sp]
                self.sp += 1
                self.pc += 2
            elif IR is self.CALL:
                """
                Calls a subroutine at the address stored in the register.
                    1. The address of the instruction directly after CALL is
                    pushed onto the stack. This allows us to return to where
                    we left off when the subroutine finishes executing.
                    2. The PC is set to the address stored in the given
                    register. We jump to that location in RAM and execute the
                    first instruction in the subroutine. The PC can move
                    forward or backwards from its current location.
                """
                # Push return address onto the stack
                return_address = self.pc + 2
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = return_address
                # Set PC to the value in the register
                self.pc = self.reg[operand_a]
            elif IR is self.RET:
                # Return from subroutine.
                # Pop the value from the top of the stack and store it in the PC.
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
            elif IR in alu_dict:
                self.alu(alu_dict[IR], operand_a, operand_b)
                self.pc += 3
            elif IR is self.HLT:
                # Halt the CPU (and exit the emulator)
                break
            else:
                print(f'Error: Unknown command: {IR}')
                sys.exit(1)