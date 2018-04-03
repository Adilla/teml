#!/usr/bin/env python

import sys
from src.frontends.ivie_frontend import *
from src.transformations.transformations import *
from src.backends.C_backend import *

from redbaron import RedBaron

import re 

def preprocess_ivie(ivie_source):
    """ Modifier of syntax to fit fully in RedBaron """

    # Remove space between perm and iterator name
    ivie_source = ivie_source.replace("perm ", "perm")

   # Transform <> into ()
    ivie_source = ivie_source.replace("<", "(").replace(">", ")")
 
    return ivie_source

def parse_ivie_source(iviesrc):
    """ Parser of Ivie source using RedBaron.
    Ivie syntax strongly resembles Python syntax. Therefore 
    Ivie source is preprocessed to fully fit in Python syntax
    so that RedBaron can recognize every token.
    
    Returns Ivie FST as a Python FST.  """

    ivieprog = None
    with open(iviesrc, "r") as source:
       newsource = preprocess_ivie(source.read())
       ivieprog = RedBaron(newsource)
    return ivieprog


def main():
    ivie_source = sys.argv[1]
    fst = parse_ivie_source(ivie_source)
    program = process_FST(fst)



    
    build_isl_loop_schedule(program)

    execute_scheduler(program)

    #build_isl_domain(program)
    
    #print program.debug_print()


    #set_allocation_modes(program)
    #backend(program)
    
    ##print prettyprint_CFD_C(program)
    print prettyprint_C(program)
if __name__ == "__main__":
    main()
