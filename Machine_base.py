import sys

from ControlUnit_base import ControlUnit
from ISA_base import read_machine_code


def read_from_input(data_input):
    with open(data_input, encoding="utf-8") as file:
        data = file.read()
    return {1: [(1, data[i]) for i in range(len(data))]}


def main(source, data_input):
    data, code, start = read_machine_code(source)
    data_input = read_from_input(data_input)
    cu = ControlUnit(data, code, data_input, start)
    cu.start()
    print("".join(cu.data_path.out_buffer[0]))


if __name__ == "__main__":
    assert (
        len(sys.argv) == 3
    ), "Wrong arguments: Machine_base.py <source_file> <input_file>"
    _, source, data_input = sys.argv
    main(source, data_input)
