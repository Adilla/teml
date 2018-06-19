import sys 
#from src.frontends.c_frontend import *

import re

from src.frontends.c_frontend import *
from pycparser import parse_file, c_ast, c_parser, c_generator
from redbaron import RedBaron
import subprocess
import copy

import sys


def parse_c_source(csrc):
    """ Parser of C source using pycparser. """

    string = None
    with open(csrc, "r") as source:
        string = source.read()

    ## Generate AST
    parser = c_parser.CParser()
    ast = parser.parse(string)
    return ast 



def main():
    c_source = sys.argv[1]
    ast = parse_c_source(c_source)

    for ex in ast.ext:
        length = len(ex.body.block_items)
        AST_to_Ivie(ex.body.block_items[:length-1], "", c_source.replace(".c", ".ivie"))



if __name__ == "__main__":
    main()
