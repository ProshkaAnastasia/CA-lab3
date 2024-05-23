
class ALU:

    def __init__(self):
        self.operations = {
            "add": self.add,
            "cmp": self.compare,
            "inc_l": self.inc_left,
            "inc_r": self.inc_right,
            "dec_l": self.dec_left,
            "dec_r": self.dec_right,
            "skip_r": self.skip_left,
            "skip_l": self.skip_right
        }

    def add(self):
        self.result = self.left_input + self.right_input
        self.set_flags(self.get_flags(self.result))

    def compare(self):
        tmp = self.left_input - self.right_input
        self.set_flags(self.get_flags(tmp))

    def inc_left(self):
        self.result = self.left_input + 1
        self.set_flags(self.get_flags(self.result))
    
    def inc_right(self):
        self.result = self.right_input + 1
        self.set_flags(self.get_flags(self.result))

    def dec_left(self):
        self.result = self.left_input - 1
        self.set_flags(self.get_flags(self.result))
    
    def dec_right(self):
        self.result = self.right_input - 1
        self.set_flags(self.get_flags(self.result))

    def skip_left(self):
        self.result = self.left_input
        self.set_flags(self.get_flags(self.result))

    def skip_right(self):
        self.result = self.right_input
        self.set_flags(self.get_flags(self.result))

    flags = {
        "N": False,
        "N": False
    }

    left_input = None
    right_input = None
    result = None
    operation = None

    def execute(self):
        self.operations[self.operation]()

    def configure_operation(self, left, right, operation):
        self.left_input = left
        self.right_input = right
        self.operation = operation

    def get_flags(self, result):
        return [result < 0, result == 0]

    def set_flags(self, flags):
        self.flags["N"] = flags[0]
        self.flags["Z"] = flags[1]
