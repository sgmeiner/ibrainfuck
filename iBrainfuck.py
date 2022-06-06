#!/usr/bin/env python3
"""Brainfuck interpreter module.

usage:
    (1) create new class instance, feed raw code into it
    (2) run parser
    (3) run program / debug-run program

The parser does some preprocessing which makes code execution safer and
much faster.

to-do:
- implement dialects
- implement GUI
- cli args
- single step debugger
- arbitrary code source
- arbitrary output sink
- debugger ASCII-Code view
- debugger back stepping mode
- code&data blob format
- i/o testing, dialect sniffer
- preprocessor / parser (bracket matching, comment cleanup, stats)
"""

import os


class bf_program:
    """Run a brainfuck program and serve input / output."""

    def __init__(self, prog="", debugmode=False):
        """Initialize runtime environment."""
        # Hello World!
        testprog = ("++++++++++ [ >+++++++>++++++++++>+++>+<<<<- ] >++."
                    ">+. +++++++. . +++. >++. <<+++++++++++++++. >. +++."
                    " ------. --------. >+. >. +++. ")
        self.codestr = testprog if prog == "" else prog
        self.cleancode = []
        self.brackets = []
        self.cstats = {}
        self.data = [0] * 30000
        self.output_cache = []
        self.isdebug = debugmode
        self.commands = {
                        ">": {
                             "name": "inc_dpointer",
                             "method": self.__inc_dpointer,
                             "help": (
                                     "Increment the data pointer (to point "
                                     "to the next cell to the right)."
                                     )
                             },
                        "<": {
                             "name": "dec_dpointer",
                             "method": self.__dec_dpointer,
                             "help": (
                                     "Decrement the data pointer (to point"
                                     "to the next cell to the left)."
                                     )
                             },
                        "+": {
                             "name": "inc_dbyte",
                             "method": self.__inc_dbyte,
                             "help": (
                                     "Increment (increase by one) the "
                                     "byte at the data pointer."
                                     )
                             },
                        "-": {
                             "name": "dec_dbyte",
                             "method": self.__dec_dbyte,
                             "help": (
                                     "Decrement (decrease by one) the "
                                     "byte at the data pointer."
                                     )
                             },
                        ".": {
                             "name": "out_dbyte",
                             "method": self.__out_dbyte,
                             "help": "Output the byte at data pointer."
                             },
                        ",": {
                             "name": "in_dbyte",
                             "method": self.__in_dbyte,
                             "help": (
                                     "Accept one byte of input, storing "
                                     "its value in the byte at the "
                                     "data pointer."
                                     )
                             },
                        "[": {
                             "name": "jzf_block",
                             "method": self.__jzf_block,
                             "help": (
                                     "If the byte at the data pointer is "
                                     "zero, then instead of moving the "
                                     "instruction pointer forward to the "
                                     "next command, jump it forward to the "
                                     "command after matching ] command."
                                     )
                             },
                        "]": {
                             "name": "jzb_block",
                             "method": self.__jzb_block,
                             "help": (
                                     "If the byte at the data pointer is "
                                     "nonzero, then instead of moving the "
                                     "instruction pointer forward to the "
                                     "next command, jump it back to the "
                                     "command after the matching "
                                     "[ command."
                                     )
                             }
                        }
        self.dialect = {
                       "EOF": " ",
                       "linebreak": " ",
                       "len_data": 30000
                       }

    def parse_code(self):
        """Parse code, check for problems and do a light static analysis.

        returns: clean code, bracket lookup table, code statistics dict
        """
        # prepare data structures
        self.cleancode.clear()
        self.brackets.clear()
        self.cstats.clear()
        self.cstats = {
                      "num_char": {
                                  ">": 0,
                                  "<": 0,
                                  "+": 0,
                                  "-": 0,
                                  ".": 0,
                                  ",": 0,
                                  "[": 0,
                                  "]": 0,
                                  "comment": 0,
                                  "code": 0
                                  },
                      "max_bracket_depth": 0
                      }

        # analyze code
        bracket_level = 0
        for char in self.codestr:
            if char in self.commands.keys():
                self.cstats["num_char"][char] += 1
                self.cstats["num_char"]["code"] += 1
                self.cleancode.append(char)

                # bracket matching
                if char == "[":
                    bracket_level += 1
                    self.brackets.append({
                                         "dir": 1,
                                         "pos": len(self.cleancode) - 1,
                                         "match": 0
                                         })
                    self.cstats["max_bracket_depth"] = max(
                            bracket_level,
                            self.cstats["max_bracket_depth"]
                            )

                elif char == "]":
                    bracket_level -= 1
                    self.brackets.append({
                                         "dir": -1,
                                         "pos": len(self.cleancode) - 1,
                                         "match": 0
                                         })
                # if we have an unmatched bracket we're off
                if bracket_level < 0:
                    raise ValueError()
                    return self.cleancode, self.brackets, self.cstats

            else:
                self.cstats["num_char"]["comment"] += 1

        # any unmatched brackets?
        if bracket_level:
            raise ValueError()
            return self.cleancode, self.brackets, self.cstats
        else:
            # safe to complete lookup table
            for i, bracket in enumerate(self.brackets):
                if (bracket["dir"] + 1):
                    local_bracket_level = 0
                    for candidate in self.brackets[i:]:
                        local_bracket_level += candidate["dir"]
                        if not local_bracket_level:
                            # we found the matching candidate
                            self.brackets[i]["match"] = candidate["pos"]
                            candidate["match"] = self.brackets[i]["pos"]
                            break

        return self.cleancode, self.brackets, self.cstats

    def __inc_dpointer(self, ip, dp):
        """Increase data pointer by one."""
        return (ip + 1), (dp + 1)

    def __dec_dpointer(self, ip, dp):
        """Decrease data pointer by one."""
        return (ip + 1), (dp - 1)

    def __inc_dbyte(self, ip, dp):
        """Increase byte at data pointer by one."""
        self.data[dp] = (self.data[dp] + 1) & 255
        return (ip + 1), dp

    def __dec_dbyte(self, ip, dp):
        """Decrease byte at data pointer by one."""
        self.data[dp] = (self.data[dp] - 1) & 255
        return (ip + 1), dp

    def __out_dbyte(self, ip, dp):
        """Output one byte (ASCII) from data pointer to stdout."""
        if not self.isdebug:
            # no debug mode? print now
            print(chr(self.data[dp]), end="")
        self.output_cache.append(self.data[dp])
        return (ip + 1), dp

    def __in_dbyte(self, ip, dp):
        """Read one character from stdin and write at current data pointer."""
        in_byte = input("pls input one character: ")
        if in_byte == "":
            self.data[dp] = 0
        else:
            self.data[dp] = ord(in_byte[0])
        return (ip + 1), dp

    def __jzf_block(self, ip, dp):
        """Jump if zero, forward to 1st instruction after block end."""
        if self.data[dp]:
            return (ip + 1), dp
        else:
            return (list(self.codestr[ip:]).index("]") + ip + 1), dp

    def __jzb_block(self, ip, dp):
        """Jump if zero, backward to 1st instruction after block begin."""
        if self.data[dp]:
            return (self.codestr.rfind("[", 0, ip) + 1), dp
        else:
            return (ip + 1), dp

    def __fixlenstr(self, obj, length, fill=" "):
        """Convert obj to str of fixed length, if possible."""
        shortstr = str(obj)
        longstr = "".join([fill] * (length - len(shortstr))) + shortstr
        return longstr

    def debug_output(self, ip, dp):
        """Provide verbose output and single-step-execution in debug mode."""
        os.system("clear")
        print(f"Output ({len(self.output_cache)} characters): "
              + "".join([chr(character) for character in self.output_cache])
              + "\n")
        print(f"Instruction Pointer: {ip}, Data Pointer: {dp}\n")
        print("Code:", self.codestr)
        print("IP:   " + "".join(["-"] * (ip)) + "|"
              + "".join(["-"] * (len(self.codestr) - ip - 2)), "\n")
        print("Data: " + "|".join([self.__fixlenstr(elm, 3)
              for elm in self.data[:30]]))
        print("DP:   " + "".join(["--- "] * (dp)) + "||| "
              + "".join(["--- "] * (30 - dp - 1)), "\n")
        input("<enter> to execute ...")
        return None

    def run(self):
        """Run the program."""
        # startup
        data_pt = 0
        instr_pt = 0
        os.system("clear")
        print("Output: ")

        # walk through code string
        while instr_pt < len(self.codestr):
            if self.codestr[instr_pt] in self.commands.keys():
                # execute valid commands, ...
                if self.isdebug:
                    self.debug_output(instr_pt, data_pt)
                instr_pt, data_pt = (self.commands[self.codestr[instr_pt]][
                                                "method"](instr_pt, data_pt))
            else:
                # ... ignore other stuff.
                if not self.isdebug:
                    if self.codestr[instr_pt] == "#":
                        self.debug_output(self, instr_pt, data_pt)
                        print("Output: " + ("".join([chr(character)
                              for character in self.output_cache])))
                instr_pt += 1

        # exit; interpret byte lastly pointed to as return value
        if self.isdebug:
            self.debug_output(instr_pt, data_pt)
        print("\n\nProgram finished.")
        return self.data[data_pt]


def run_tests():
    """Test the modules class(-es), if not imported."""
    testprog = bf_program(debugmode=True)
    print("Got one instance: ", type(testprog))
    print("Code currently is: ", testprog.codestr, "\n")
    print(f"\n{testprog.check_codestr()} non-command characters in code.")
    print(f"Return value: {testprog.run()}.")
    return None


if __name__ == "__main__":
    run_tests()
