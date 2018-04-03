import sys
from src.frontends.tml_frontend import *

from redbaron import RedBaron
import re

def preprocess_source(src):
    """ Removes all syntactic sugar for the sources to be fully Python-compliant """
    
    src = src.replace(" -> ", ",")

    return src

def parse_tml(src):
    """ Parses TeML source with RedBaron 

    Returns a Python full syntax tree (FST)
    """


    prog = None
    with open(src, "r") as source:
        tmp = preprocess_source(source.read())
        prog = RedBaron(tmp)

    return prog


def main():
    source = sys.argv[1]
    fst = parse_tml(source)
    prog = process_FST(fst)

    #print prog.debug_print()


if __name__ == "__main__":
    main()
