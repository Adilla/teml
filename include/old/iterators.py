from copy import deepcopy, copy
from termcolor import colored
import sys


class Iterator():

    rank = None
    vec_hints = None
    parent = None
    kind = None
    permutable = None
    garbage = False
    parallelism = None
    schedule = None
    private_variables = None
    tile_parent = None
    tilesize = None
    unroll_factor = None
    vector_factor = None
    peel_begin_factor = None
    peel_end_factor = None
    reversed = None
    axe_traversor_parent = None
    axe_traversal = False
    virtualized = []


    def __init__(self, rank, minbound, maxbound, stride):
        self.name = "i" + str(rank)
        self.rank = rank
        self.minbound = minbound
        self.maxbound = maxbound
        self.stride = stride

    def debug_print(self):
        string = colored("ITERATOR:", "blue",  attrs=["bold"]) + colored(" " + self.name, attrs=["bold"]) + " {" + self.minbound + ", " + self.maxbound + ", " + self.stride + "}"
        return string



    
    def set_axe_traversal(self, boolean):
        self.axe_traversal = True

    def set_permutability(self, boolean):
        self.permutable = boolean
        
    def set_kind(self, kind):
        self.kind = kind

    def set_parallelism(self, paraltype):
        self.parallelism = paraltype

    def set_schedule(self, chunksize):
        self.schedule = chunksize

    def set_private_variables(self, varlist):
        self.private_variables = varlist

    def set_axe_traversor_parent(self, parent):
        self.axe_traversor_parent = parent

    def set_tile_parent(self, parent):
        self.tile_parent = parent

    def set_tile_size(self, size):
        self.tilesize = size

    def update_minbound(self, new):
        self.minbound = new

    def update_maxbound(self, new):
        self.maxbound = new

    def update_stride(self, new):
        self.stride = new

    def set_unroll_factor(self, factor):
        self.unroll_factor = factor

    def mark_as_garbage(self):
        self.garbage = True

    def add_virtualized(self, iterator):
        self.virtualized.append(iterator)

    def set_reversed(self, boolean):
        self.reversed = boolean

    def set_peel_begin_factor(self, factor):
        self.peel_begin_factor = factor

    def set_peel_end_factor(self, factor):
        self.peel_end_factor = factor


        

    """
    def prettyprint_C_dimension(self, newname, indent):
        parallinfo = ""
        string = ""
        if self.garbage == False:
            if self.kind == "piter":
                if self.paralellism == "THRD":
                    parallinfo += "#pragma omp parallel for " + indent
                
                    if self.private_variables != None:
                        parallinfo += "private(" 
                        for pri in self.private_variables[1:]:
                            parallinfo += pri + ","
                        parallinfo += self.private_variables[len(self.private_variables)]

                        parallinfo += ") "
                    if self.schedule != None:
                        ## TODO: Change schedule according to tile sizes
                        parallinfo += "schedule(static, " + self.schedule + ")\n"

                if self.parallelism == "VEC":
                    ### Test
                    parallinfo += "#pragma omp for simd\n" 
                    
            parallinfo += indent

        
            string += parallinfo

            if self.tile_parent != None:
                string += "for (" + self.tile_parent.name + " = " + self.tile_parent.minbound
                string += "; " + self.tile_parent.name + " < " + self.tile_parent.maxbound + ";"
                string += self.tile_parent.name + " += " + self.tile_parent.stride + ") {\n"

        string += "for (" + newname + " = " + self.minbound
        string += "; " + newname + " < " + self.maxbound + ";"
        string += newname + " += " + self.stride + ") {\n"
    """

