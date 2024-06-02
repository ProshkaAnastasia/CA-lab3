from enum import Enum
from ALU_base import ALU
from ISA_base import registers

class Selector(Enum):
    ALU = 0
    MEMORY = 1
    INPUT = 2
    DR = 3
    REGISTER = 4

class DataPath:
    def __init__(self, data, in_buf):
        self.registers = {"r" + str(i): 0 for i in range(32)}
        self.hidden_registers = {
            "dr": 0,
            "ar": 0,
            "sp": 0,
            "ps": {
                "N": False,
                "Z": False,
                "W": False,
                "I": False
            }
        }
        self.data_memory = data
        self.alu = ALU()
        self.in_ports = [1]
        self.out_ports = [0]
        self.in_buffer = in_buf
        self.out_buffer = {i: [] for i in self.out_ports}
        self.current_in_port = 1
        self.current_out_port = 0

    def mem_write(self):
        self.data_memory[self.hidden_registers["ar"]] = self.hidden_registers["dr"]

    def mem_read(self):
        self.signal_latch_dr(Selector.MEMORY)

    def input(self, port):
        self.hidden_registers["dr"] = ord(self.in_buffer[port].pop(0)[1])

    def output(self, port):
        self.out_buffer[port].append(chr(self.hidden_registers["dr"]))

    def push(self, arg):
        current_sp = self.hidden_registers["sp"]
        self.hidden_registers["sp"] = current_sp - 1 if current_sp > 0 else len(self.data_memory) - 1
        self.hidden_registers["ar"] = self.hidden_registers["sp"]
        self.execute_ALU("skip_left", arg, "0")
        self.signal_latch_dr(Selector.ALU)
        self.mem_write()

    def pop(self, arg):
        self.execute_ALU("skip_right", "0", "sp")
        self.signal_latch_ar()
        self.mem_read()
        current_sp = self.hidden_registers["sp"]
        self.hidden_registers["sp"] = current_sp + 1 if current_sp < len(self.data_memory) - 1 else 0
        self.execute_ALU("skip_right", "0", "dr")
        if arg in self.registers:
            self.signal_latch_register(arg)

    def signal_latch_sp(self):
        self.hidden_registers["sp"] = self.alu.result
    
    def signal_latch_register(self, target: str):
        if not target in registers:
            raise Exception(f"Wrong register {target}")
        self.registers[target] = self.alu.result

    def signal_latch_dr(self, sel):
        if not sel in [Selector.ALU, Selector.MEMORY, Selector.INPUT]:
            raise Exception("Wrong selector for DR")
        match sel:
            case Selector.ALU:
                self.hidden_registers["dr"] = self.alu.result
            case Selector.MEMORY:
                self.hidden_registers["dr"] = self.data_memory[self.hidden_registers["ar"]]
            case Selector.INPUT:
                self.hidden_registers["dr"] = self.in_buffer[self.current_in_port]

    def signal_latch_ar(self):
        self.hidden_registers["ar"] = self.alu.result

    def left_mux_ALU(self, value):
        self.alu.left = value

    def right_mux_ALU(self, value):
        self.alu.right = value

    def configure_ALU(self, left = 0, right = 0):
        self.left_mux_ALU(left)
        self.right_mux_ALU(right)

    def is_number_argument(self, arg: str):
        if arg.isdigit():
            return self.alu.min <= int(arg) and int(arg) <= self.alu.max
        else:
            return False
    def setup_ALU(self, left: str, right: str):
        if left in self.registers:
            self.left_mux_ALU(self.registers[left])
        elif left in self.hidden_registers:
            self.left_mux_ALU(self.hidden_registers[left])
        elif self.is_number_argument(left):
            self.left_mux_ALU(int(left))
        else:
            self.left_mux_ALU(0)
        if right in self.registers:
            self.right_mux_ALU(self.registers[right])
        elif right in self.hidden_registers:
            self.right_mux_ALU(self.hidden_registers[right])
        elif self.is_number_argument(right):
            self.right_mux_ALU(int(right))
        else:
            self.right_mux_ALU(0)

    def execute_ALU(self, operation, left: str = "0", right: str = "0"):
        self.setup_ALU(left, right)
        self.alu.execute(operation)

    def exec_ALU(self, operation, left, right):
        self.configure_ALU(left, right)
        self.alu.execute(operation)

    def signal_latch_ps(self):
        self.hidden_registers["ps"]["Z"] = self.alu.flags["Z"]
        self.hidden_registers["ps"]["N"] = self.alu.flags["N"]
        self.hidden_registers["ps"]["W"] = self.alu.flags["W"]


