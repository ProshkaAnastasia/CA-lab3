from ControlUnit_base import ControlUnit
from ISA_base import read_machine_code

target = "./text/machine/hello_user_name"
data, code, start = read_machine_code(target)
print(ord("\n"))
cu = ControlUnit(data, code, {1: [(1, 'A'), (2, 'n'), (3, 'a'), (4, 's'), (5, 't'), (6, 'a'), (7, 's'), (8, 'i'), (9, 'a')]}, start)
cu.start()
print(cu.data_path.out_buffer[0])
