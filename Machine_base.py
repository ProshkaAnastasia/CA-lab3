import sys
from ControlUnit_base import ControlUnit
from ISA_base import read_machine_code

#target = "./text/machine/hello_user_name"
#data, code, start = read_machine_code(target)
#cu = ControlUnit(data, code, {1: [(1, 'A'), (2, 'n'), (3, 'a'), (4, 's'), (5, 't'), (6, 'a'), (7, 's'), (8, 'i'), (9, 'a')]}, start)
#cu.start()
#print(cu.data_path.out_buffer[0])

def read_from_input(input):
    with open(input, 'r', encoding='utf-8') as file:
        data = file.read()
    result = {
        1: [
            (1, data[i]) for i in range(len(data))
        ]
    }
    return result

def main(source, input):
    data, code, start = read_machine_code(source)
    input = read_from_input(input)
    cu = ControlUnit(data, code, input, start)
    cu.start()
    print(''.join(cu.data_path.out_buffer[0]))

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: Machine_base.py <source_file> <input_file>"
    _, source, input = sys.argv
    #source = "./code/binary/prob1"
    #input = "./code/input/prob1.txt"
    main(source, input)
