"""GCC executing library"""
import os
import subprocess

import requests


class GCCRunner:
    """GCC execution helper class"""

    def __init__(self):
        self.C_COMPILER = "gcc"
        self.CXX_COMPILER = "g++"

        self.C_FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-std=c11"]
        self.CXX_FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-std=c++1z"]

        self.FILE_PATH = os.path.join(os.path.split(
            os.path.realpath(__file__))[0], "tmp")
        if not os.path.exists(self.FILE_PATH):
            os.makedirs(self.FILE_PATH)
        self.C_FILE_PATH = os.path.join(self.FILE_PATH, "tmp.c")
        self.CXX_FILE_PATH = os.path.join(self.FILE_PATH, "tmp.cpp")
        self.OUTPUT_FILE = os.path.join(self.FILE_PATH, "tmp.exe")

        self.C_HEADERS = ["stdio.h", "time.h", "stdlib.h", "string.h"]
        self.CXX_HEADERS = ["iostream", "array", "vector",
                            "algorithm", "string", "chrono", "random"]

        self.C_HEADERS_CODE = '\n'.join(
            ["#include <{}>".format(x) for x in self.C_HEADERS]) + '\n'
        self.CXX_HEADERS_CODE = '\n'.join(
            ["#include <{}>".format(x) for x in self.CXX_HEADERS]) + '\n'
        self.CXX_HEADERS_CODE = '\n'.join(
            ["#include <{}>".format(x) for x in self.CXX_HEADERS]) + '\n'

        self.CODE_COMMENT = "// Generated using GCCRunner by SteelPh0enix\n"

    def run_c_code(self, code: str) -> dict:
        """Runs C code in main() function
        :rtype: dict
        :param code: Code to execute"""

        runcode = self.CODE_COMMENT + self.C_HEADERS_CODE + \
                  "\nint main() {\n" + code + "\n}\n"
        return self.compile_and_run_c(runcode)

    def run_cxx_code(self, code: str) -> dict:
        """Runs C + + code in main() function
        :rtype: dict
        :return: look: compile_and_run_cxx"""

        runcode = self.CODE_COMMENT + self.CXX_HEADERS_CODE + \
                  "\nint main() {\n" + code + "\n}\n"
        return self.compile_and_run_cxx(runcode)

    def compile_and_run_c(self, code: str) -> dict:
        """Executes the C code.
        :rtype: dict
        :param code: Code to execute(full file)
        :return: dict with objects 'compilation', and (if compilation was successful) 'execution'.
        Both objects contain keys 'stdout', 'stderr' and 'retcode'."""

        with open(self.C_FILE_PATH, mode="w") as c_file:
            c_file.write(code)

        comp_stdout, comp_stderr, comp_code = run_and_get_output(
            [self.C_COMPILER] + self.C_FLAGS + ["-o", self.OUTPUT_FILE, self.C_FILE_PATH])

        ret_dict = {
            'compilation':
                { 'stdout': comp_stdout, 'stderr': comp_stderr.replace(self.C_FILE_PATH + ':', ""), 'retcode': comp_code }
        }

        if comp_code != 0:
            return ret_dict

        exec_stdout, exec_stderr, exec_code = run_and_get_output(
            [self.OUTPUT_FILE])

        ret_dict['execution'] = {
            'stdout': exec_stdout, 'stderr': exec_stderr, 'retcode': exec_code
        }

        return ret_dict

    def compile_and_run_cxx(self, code: str) -> dict:
        """Executes the C + + code.
        :rtype: dict
        :param code: Code to execute(full file)
        :return: dict with objects 'compilation', and (if compilation was successful) 'execution'.
        Both objects contain keys 'stdout', 'stderr' and 'retcode'."""

        with open(self.CXX_FILE_PATH, mode="w") as cxx_file:
            cxx_file.write(code)

        comp_stdout, comp_stderr, comp_code = run_and_get_output(
            [self.CXX_COMPILER] + self.CXX_FLAGS + ["-o", self.OUTPUT_FILE, self.CXX_FILE_PATH])

        ret_dict = {
            'compilation':
                { 'stdout': comp_stdout, 'stderr': comp_stderr.replace(self.CXX_FILE_PATH + ':', ""), 'retcode': comp_code }
        }

        if comp_code != 0:
            return ret_dict

        exec_stdout, exec_stderr, exec_code = run_and_get_output(
            [self.OUTPUT_FILE])

        ret_dict['execution'] = {
            'stdout': exec_stdout, 'stderr': exec_stderr, 'retcode': exec_code
        }

        return ret_dict


def run_and_get_output(arguments: list) -> tuple:
    """Runs the program and returns(stdout, stderr, return_code) tuple
    :rtype: tuple(str, str, int)
    :param arguments: list with executable path and it's arguments
    :return: Tuple with stdout and stderr content, and return code of program"""
    proc = subprocess.Popen(
        arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode('utf-8'), err.decode('utf-8'), proc.returncode


def post_on_hastebin(content: str) -> str:
    """Helper function.
    Posts the stuff on Hastebin, returns URL.
    Yea, this is copy & paste from hastebin.py
    https://github.com/LyricLy/hastebin.py/blob/master/hastebin/hastebin.py"""
    post = requests.post("https://hastebin.com/documents", data=content.encode())
    return str("https://hastebin.com/" + post.json()["key"])


def prepare_message(data: dict, max_len=50) -> str:
    """Function preparing the compilation data in human-readable form"""

    return_message = ''
    if data['compilation']['retcode'] != 0:
        return_message += 'Compilation error! Code: {}\n'.format(data['compilation']['retcode'])
        if len(data['compilation']['stderr']) > max_len:
            return_message += 'Log too long, go there: {}\n'.format(post_on_hastebin(data['compilation']['stderr']))
        else:
            return_message += 'Log: "{}"\n'.format(data['compilation']['stderr'])
    else:
        if len(data['execution']['stdout']) > max_len:
            return_message += 'Output too long, you can find it here: {}\n'.format(
                post_on_hastebin(data['execution']['stdout']))
        else:
            return_message += 'Output: "{}"\n'.format(data['execution']['stdout'])
        if data['execution']['retcode'] != 0:
            return_message += 'Return code is {}\n'.format(data['execution']['retcode'])

    return return_message
