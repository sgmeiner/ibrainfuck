#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os

""" brainfuck interpreter module """


class bf_program:
    """ brainfuck program class """

    def __init__(self, debugmode=False):
        """ initialize brainfuck data """
        # Hello World!
        teststr_1 = ("++++++++++ [ >+++++++>++++++++++>+++>+<<<<- ] >++."
                        + ">+. +++++++. . +++. >++. <<+++++++++++++++. >. +++."
                        + " ------. --------. >+. >. +++. ")
        # add 2 and 5
        teststr_2 = "++ > +++++ [<+>-] ++++ ++++ [<+++ +++> -]<."
        teststr_3 = (">>,[>>,]<<[[<<]>>>>[<<[>+<<+>-]>>[>+<<<<[->]>[<]>>-]<<<"
                    "[[-]>>[>+<-]>>[<<<+>>>-]]>>[[<+>-]>>]<]<<[>>+<<-]<<"
                    "]>>>>[.>>]")
        teststr_4 = ">+[ <[ [>>+<<-]>[<<+<[->>+[<]]>>>[>]<<-]<<< ]>>[<<+>>-]<[>+<-]>[>>]<, ]<<<[<+<]>[>.>]"
        teststr_5 = ("+++[>+++++<-]>[>+>+++>+>++>+++++>++<[++<]>---]>->-.[>++>+<<--]>--.--.+.>"
                    ">>++.<<.<------.+.+++++.>>-.<++++.<--.>>>.<<---.<.-->-.>+.[+++++.---<]>>"
                    "[.--->]<<.<+.++.++>+++[.<][http://www.hevanet.com/cristofd/brainfuck/]<.")
        # sorting
        teststr_6 = ">,[>,]+[<[-<]>[>]>[<-[>]<.>>]<<+]"

        teststr_7 = ">,>+++++++++,>+++++++++++[<++++++<++++++<+>>>-]<<.>.<<-.>.>.<<."

        # codestr content now is for testing only
        self.codestr = teststr_1
        self.data = [0] * 30000
        self.output_cache = []
        self.isdebug = debugmode
        self.commands = {
                        ">": {"name": "inc_dpointer",
                                "method": self.__inc_dpointer,
                              "help": ("Increment the data pointer (to point "
                                        "to the next cell to the right).")},
                        "<": {"name": "dec_dpointer",
                                "method": self.__dec_dpointer,
                                "help": ("Decrement the data pointer (to point"
                                        "to the next cell to the left).")},
                        "+": {"name": "inc_dbyte",
                                "method": self.__inc_dbyte,
                                "help": ("Increment (increase by one) the byte"
                                        " at the data pointer.")},
                        "-": {"name": "dec_dbyte",
                                "method": self.__dec_dbyte,
                                "help": ("Decrement (decrease by one) the byte"
                                        "at the data pointer.")},
                        ".": {"name": "out_dbyte",
                                "method": self.__out_dbyte,
                                "help": "Output the byte at data pointer."},
                        ",": {"name": "in_dbyte",
                                "method": self.__in_dbyte,
                                "help": ("Accept one byte of input, storing "
                                        "its value in the byte at the "
                                        "data pointer.")},
                        "[": {"name": "jzf_block",
                                "method": self.__jzf_block,
                                "help": ("If the byte at the data pointer is "
                                        "zero, then instead of moving the "
                                        "instruction pointer forward to the "
                                        "next command, jump it forward to the "
                                        "command after matching ] command.")},
                        "]": {"name": "jzb_block",
                                "method": self.__jzb_block,
                                "help": ("If the byte at the data pointer is "
                                        "nonzero, then instead of moving the "
                                        "instruction pointer forward to the "
                                        "next command, jump it back to the "
                                        "command after the matching "
                                        "[ command.")}
                        }

    def check_codestr(self):
        """ check wether code str contains non-command characters.
        takes no args, returns
        0 (false),  if no non-command character
        numer of non-command characters, if there were any """

        non_command = 0
        for command in self.codestr:
            if command not in self.commands.keys():
                non_command += 1
        return non_command

    def __inc_dpointer(self, ip, dp):
        """ increase data pointer by one """
        return (ip + 1), (dp + 1)

    def __dec_dpointer(self, ip, dp):
        """ decrease data pointer by one """
        return (ip + 1), (dp - 1)

    def __inc_dbyte(self, ip, dp):
        """ increase byte at data pointer by one """
        self.data[dp] = (self.data[dp] + 1) & 255
        return (ip + 1), dp

    def __dec_dbyte(self, ip, dp):
        """ decrease byte at data pointer by one """
        self.data[dp] = (self.data[dp] - 1) & 255
        return (ip + 1), dp

    def __out_dbyte(self, ip, dp):
        """ output one byte (ASCII) from data pointer to stdout """
        if not self.isdebug:
            # no debug mode? print now
            print(chr(self.data[dp]), end="")
        self.output_cache.append(self.data[dp])
        return (ip + 1), dp

    def __in_dbyte(self, ip, dp):
        """ read one character from stdin and write at current data pointer """
        in_byte = input("pls input one character: ")
        if in_byte == "":
            self.data[dp] = 0
        else:
            self.data[dp] = ord(in_byte[0])
        return (ip + 1), dp

    def __jzf_block(self, ip, dp):
        """ jump if zero forward to 1st instruction after block end """
        if self.data[dp]:
            return (ip + 1), dp
        else:
            return (list(self.codestr[ip:]).index("]") + ip + 1), dp

    def __jzb_block(self, ip, dp):
        """ jump if zero backward to 1st instruction after block begin """
        if self.data[dp]:
            return (self.codestr.rfind("[", 0, ip) + 1), dp
        else:
            return (ip + 1), dp

    def __fixlenstr(self, obj, length, fill=" "):
        """ convert obj to str of fixed length, if possible """
        shortstr = str(obj)
        longstr = "".join([fill] * (length - len(shortstr))) + shortstr
        return longstr


    def debug_output(self, ip, dp):
        """ provide verbose output in debug mode """
        os.system("cls")
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
        """ run the program """
        # startup
        data_pt = 0
        instr_pt = 0
        os.system("cls")
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
                        debug_output(self, ip, dp)
                        print(f"Output: "
                                + ("".join([chr(character)
                                    for character in self.output_cache])))
                instr_pt += 1

        # exit; interpret byte lastly pointed to as return value
        if self.isdebug:
            self.debug_output(instr_pt, data_pt)
        print("\n\nProgram finished.")
        return self.data[data_pt]


def run_tests():
    """ test the modules classes, if not imported """
    testprog = bf_program(debugmode=True)
    print("Got one instance: ", type(testprog))
    print("Code currently is: ", testprog.codestr, "\n")
    print(f"\nCode contains {testprog.check_codestr()} non-command characters.")
    print(f"Return value: {testprog.run()}.")
    return None


if __name__ == "__main__":
    run_tests()
