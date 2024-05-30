import invoke
import pathlib
import sys
import os
import shutil
import re
import glob

def print_banner(msg):
    print("==================================================")
    print("= {} ".format(msg))

@invoke.task()
def build_quasimodo(c):
    """Build the shared library for the sample C++ code"""
    print_banner("Building C++ Library")
    invoke.run(
        "cd .. && make all && cd python_pkg/ && cp ../libquasimodo.so ."
    )
    print("* Complete")

# Use -undefined dynamic_lookup for MACOS
def compile_python_module(cpp_name, extension_name):
    libs = "-L/opt/homebrew/lib -L/opt/homebrew/Cellar/boost/1.85.0/lib -I/opt/homebrew/Cellar/boost/1.85.0/include -L/opt/homebrew/Cellar/mpfr/4.2.1/lib -I/opt/homebrew/Cellar/mpfr/4.2.1/include -L/opt/homebrew/Cellar/gmp/6.3.0/lib -I/opt/homebrew/Cellar/gmp/6.3.0/include"
    invoke.run(
        "g++ -g -O3 -L/opt/homebrew/lib {4} -std=c++2a -w -shared -Wall -Wextra -DHAVE_CONFIG_H -Werror -Wunused-but-set-variable -fPIC -I${3}"
        "`python3.11 -m pybind11 --includes` "
        "-I {2} -I../ "
        "{0} "
        "-o {1}`python3.11-config --extension-suffix` "
        "-L. -lquasimodo -Wl,-rpath,. -undefined dynamic_lookup".format(cpp_name, extension_name, os.environ["PYTHON_INCLUDE"], os.environ["BOOST_PATH"], libs)
    )

@invoke.task()
def build_pybind11(c):
    """Build the pybind11 wrapper library"""
    print_banner("Building PyBind11 Module")
    compile_python_module("quasimodo_python_wrapper.cpp", "pyquasimodo")
    print("* Complete")

@invoke.task()
def test_pybind11(c):
    """Run the script to test PyBind11"""
    print_banner("Testing PyBind11 Module")
    invoke.run("python3 pybind11_test.py", pty=True)
