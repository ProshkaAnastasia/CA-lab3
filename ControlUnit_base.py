from DataPath_base import DataPath, Selector
from ISA_base import Opcode


class ControlUnit:
    def __init__(self, data, code, in_buf, start):
        self.counter = 0
        self.CR = 0
        self.IP = start
        self.code_memory = code
        self.data_path = DataPath(data, in_buf)
        self.active = False
        self.int_address = 0
        self.int_state = {"Z": False, "N": False, "W": False, "I": True}

    def signal_latch_ip(self):
        self.IP = self.data_path.alu.result

    def signal_read_command(self):
        self.CR = self.code_memory[self.IP]

    def start(self):
        self.active = True
        while self.active:
            self.signal_read_command()
            self.decode_and_execute()

    def print_state(self):
        dr = "dr"
        ar = "ar"
        ps = "ps"
        r = "r"
        instr = self.CR
        opcode = Opcode(int(instr[0:8], 2))
        print("=====================================================================")
        print(f"| instruction: {opcode}")
        print(f"| DR = {self.data_path.hidden_registers[dr]}")
        print(f"| AR = {self.data_path.hidden_registers[ar]}")
        print(f"| PS = {self.data_path.hidden_registers[ps]}")
        print(f"| IP = {self.IP}")
        print(f"| CR = {hex(int(self.CR, 2))}")
        for i in range(4):
            print(f"| R{i} = {self.data_path.registers[r + str(i)]}")
        print("=====================================================================")

    def interrupt(self):
        for i in self.data_path.registers:
            self.data_path.push(i)
        self.data_path.push("ps")
        self.data_path.push(str(self.IP))
        self.IP = self.int_address
        self.data_path.hidden_registers["ps"] = self.int_state

    def check_interruption(self):
        interruption = self.data_path.hidden_registers["ps"]["I"]
        for port in self.data_path.in_ports:
            buf = self.data_path.in_buffer[port]
            if not interruption and len(buf) > 0 and buf[0][0] == self.counter:
                self.data_path.current_in_port = port
                self.interrupt()
                return
        self.data_path.execute_alu("inc_right", "0", str(self.IP))
        self.signal_latch_ip()
        if not interruption:
            self.counter += 1

    def execute_addressed(self, opcode, instr):
        arg1 = "r" + str(int(instr[10:21], 2))
        if instr[8] == "1":
            arg2 = "r" + str(int(instr[21:32], 2))
            self.data_path.execute_alu("skip_left", arg2)
            self.data_path.signal_latch_ar()
        else:
            arg2 = str(int(instr[21:32], 2))
            self.data_path.execute_alu("skip_right", "0", arg2)
            self.data_path.signal_latch_ar()
        if instr[9] == "1":
            self.data_path.signal_latch_dr(Selector.MEMORY)
            self.data_path.execute_alu("skip_right", "0", "dr")
            self.data_path.signal_latch_ar()
        match opcode:
            case Opcode.ST:
                self.data_path.execute_alu("skip_left", arg1)
                self.data_path.signal_latch_dr(Selector.ALU)
                self.data_path.mem_write()
            case Opcode.LD:
                self.data_path.mem_read()
                self.data_path.execute_alu("skip_right", "0", "dr")
                self.data_path.signal_latch_register(arg1)
        self.data_path.signal_latch_ps()
        self.check_interruption()

    def execute_branch_instruction(self, opcode, arg):
        match opcode:
            case Opcode.BEQ:
                if self.data_path.hidden_registers["ps"]["Z"]:
                    self.data_path.execute_alu("skip_right", "0", arg)
                    self.signal_latch_ip()
                    return
            case Opcode.BNE:
                if not self.data_path.hidden_registers["ps"]["Z"]:
                    self.data_path.execute_alu("skip_right", "0", arg)
                    self.signal_latch_ip()
                    return
            case Opcode.JMP:
                self.data_path.execute_alu("skip_right", "0", arg)
                self.signal_latch_ip()
                return
        self.check_interruption()

    def execute_unary_instruction(self, opcode, arg):
        match opcode:
            case Opcode.INC:
                self.data_path.execute_alu("inc_left", arg)
                self.data_path.signal_latch_ps()
            case Opcode.DEC:
                self.data_path.execute_alu("dec_left", arg)
                self.data_path.signal_latch_ps()
            case Opcode.PUSH:
                self.data_path.push(arg)
            case Opcode.POP:
                self.data_path.pop(arg)
            case Opcode.PRINTI:
                self.data_path.print(arg)
        self.data_path.signal_latch_register(arg)
        self.check_interruption()

    def execute_binary_instruction(self, opcode, args):
        match opcode:
            case Opcode.ADD:
                self.data_path.execute_alu("skip_left", args[2])
                self.data_path.signal_latch_dr(Selector.ALU)
                self.data_path.execute_alu("add", args[1], args[2])
                self.data_path.signal_latch_ps()
                self.data_path.signal_latch_register(args[0])
            case Opcode.MOV:
                self.data_path.execute_alu("skip_left", args[1], "0")
                self.data_path.signal_latch_register(args[0])
            case Opcode.CMP:
                self.data_path.execute_alu("sub", args[0], args[1])
                self.data_path.signal_latch_ps()
            case Opcode.MOD:
                self.data_path.execute_alu("skip_left", args[2])
                self.data_path.signal_latch_dr(Selector.ALU)
                self.data_path.execute_alu("mod", args[1], "dr")
                self.data_path.signal_latch_ps()
                self.data_path.signal_latch_register(args[0])
            case Opcode.DIV:
                self.data_path.execute_alu("skip_left", args[2])
                self.data_path.signal_latch_dr(Selector.ALU)
                self.data_path.execute_alu("div", args[1], "dr")
                self.data_path.signal_latch_ps()
                self.data_path.signal_latch_register(args[0])
        self.check_interruption()

    def execute_io_instruction(self, opcode, args):
        match opcode:
            case Opcode.IN:
                self.data_path.input(int(args[1]))
                self.data_path.execute_alu("skip_right", "0", "dr")
                self.data_path.signal_latch_register(args[0])
            case Opcode.OUT:
                self.data_path.execute_alu("skip_left", args[0], "0")
                self.data_path.signal_latch_dr(Selector.ALU)
                self.data_path.output(int(args[1]))
        self.check_interruption()

    def execute_non_addressed(self, opcode, instr):
        a1, a2, a3 = int(instr[11:18], 2), int(instr[18:25], 2), int(instr[25:32], 2)
        arg1 = str(a1) if instr[8] == "0" else "r" + str(a1)
        arg2 = str(a2) if instr[9] == "0" else "r" + str(a2)
        arg3 = str(a3) if instr[10] == "0" else "r" + str(a3)
        if opcode in [Opcode.BEQ, Opcode.BNE, Opcode.JMP]:
            self.execute_branch_instruction(opcode, arg1)
        elif opcode in [Opcode.DEC, Opcode.INC, Opcode.PRINTI]:
            self.execute_unary_instruction(opcode, arg1)
        elif opcode in [Opcode.ADD, Opcode.MOV, Opcode.CMP, Opcode.MOD, Opcode.DIV]:
            self.execute_binary_instruction(opcode, [arg1, arg2, arg3])
        elif opcode in [Opcode.IN, Opcode.OUT]:
            self.execute_io_instruction(opcode, [arg1, arg2])
        else:
            self.execute_non_arg(opcode)

    def execute_non_arg(self, opcode):
        match opcode:
            case Opcode.HLT:
                self.active = False
            case Opcode.IRET:
                self.data_path.pop("ip")
                self.signal_latch_ip()
                self.data_path.pop("ps")
                self.data_path.hidden_registers["ps"] = self.data_path.hidden_registers[
                    "dr"
                ]
                for i in range(len(self.data_path.registers) - 1, -1, -1):
                    self.data_path.pop("r" + str(i))
        self.check_interruption()

    def decode_and_execute(self):
        instr = self.CR
        opcode = Opcode(int(instr[0:8], 2))
        if opcode in [Opcode.LD, Opcode.ST]:
            self.execute_addressed(opcode, instr)
        else:
            self.execute_non_addressed(opcode, instr)
