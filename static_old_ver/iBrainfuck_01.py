#!/usr/bin/env python3

""" brainfuck interpreter module """


class bf_program:
    """ brainfuck program class """
    def __init__(self):
        # codestr content hardcoded for testing purposes only
        self.codestr = "++ > +++++ [ < + > - ] ++++ ++++ [ < +++ +++ > -]< ."
        self.data = [0] * 30000
        self.commands = {
                        ">": {"name": "inc_dpointer", "method": self.__inc_dpointer,
                              "help": "Increment the data pointer (to point to the next cell to "
                                      + "the right)."},
                        "<": {"name": "dec_dpointer", "method": self.__dec_dpointer,
                              "help": "Decrement the data pointer (to point to the next cell to "
                                      + "the left)."},
                        "+": {"name": "inc_dbyte", "method": self.__inc_dbyte,
                              "help": "Increment (increase by one) the byte at the data pointer."},
                        "-": {"name": "dec_dbyte", "method": self.__dec_dbyte,
                              "help": "Decrement (decrease by one) the byte at the data pointer."},
                        ".": {"name": "out_dbyte", "method": self.__out_dbyte,
                              "help": "Output the byte at the data pointer."},
                        ",": {"name": "in_dbyte", "method": self.__in_dbyte,
                              "help": "Accept one byte of input, storing its value in the byte at "
                                      + "the data pointer."},
                        "[": {"name": "jzf_block", "method": self.__jzf_block,
                              "help": "If the byte at the data pointer is zero, then instead of "
                                      + "moving the instruction pointer forward to the next "
                                      + "command, jump it forward to the command after the "
                                      + "matching ] command."},
                        "]": {"name": "jzb_block", "method": self.__jzb_block,
                              "help": "If the byte at the data pointer is nonzero, then instead of "
                                      + "moving the instruction pointer forward to the next command, "
                                      + "jump it back to the command after the matching [ command."}
                        }

    def check_codestr(self):
        """ check wether code str contains non-command characters.
        takes no args, returns
        0 (false),  if no non-command character
        numer of non-command characters, if there were any """
        
        # besteht der code ausschl. aus commands?
        non_command = 0
        for command in self.codestr:
            if command not in self.commands.keys():
                non_command += 1
        return non_command

    def __inc_dpointer(self, ip, dp):
        return (ip + 1), (dp + 1)

    def __dec_dpointer(self, ip, dp):
        return (ip + 1), (dp - 1)

    def __inc_dbyte(self, ip, dp):
        self.data[dp] += 1
        return (ip + 1), dp

    def __dec_dbyte(self, ip, dp):
        self.data[dp] -= 1
        return (ip + 1), dp

    def __out_dbyte(self, ip, dp):
        print(chr(self.data[dp]), end="")
        return (ip + 1), dp

    def __in_dbyte(self, ip, dp):
        self.data[dp] = ord(input("pls input one character: ")[0])
        return (ip + 1), dp

    def __jzf_block(self, ip, dp):
        if self.data[dp]:
            return (ip + 1), dp
        else:
            return (list(self.codestr[ip:]).index("]") + 1), dp

    def __jzb_block(self, ip, dp):
        if self.data[dp]:
            return (list(self.codestr[:ip]).index("[") + 1), dp
        else:
            return (ip + 1), dp

    def run(self):
        data_pt = 0
        instr_pt = 0
        
        while instr_pt < len(self.codestr):
            if self.codestr[instr_pt] in self.commands.keys():
                # execute valid commands, ...
                instr_pt, data_pt = self.commands[self.codestr[instr_pt]]["method"](
                                                                    instr_pt, data_pt)
                print(f"IP: {instr_pt}, DP: {data_pt}")
                print(" | ".join([str(elm) for elm in self.data[:30]]))
            else:
                # ... ignore other stuff.
                instr_pt += 1
        
        print("\n\nProgram finished.")
        # interpret byte lastly pointed to as return value
        return self.data[data_pt]


def run_tests():
    """ test the modules classes, if not imported """
    testprog = bf_program()
    print("Got one instance: ", type(testprog))
    print("Code currently is: ", testprog.codestr, "\n")
    print(f"\nCode contains {testprog.check_codestr()} non-command characters.")
    print(f"Return value: {testprog.run()}.")
    return None


if __name__ == "__main__":
    run_tests()
