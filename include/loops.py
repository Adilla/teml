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



class LoopBox():
    def __init__(self, label, loopnest):
        self.label = label
        self.loopnest = loopnest

    

class Loop():
    """ Types
    iterators: list of Iterators
    body: list of either Statement or Loop
    """
    
    def __init__(self, iterator, body):
        self.iterator = iterator
        self.body = body
        self.outer_pre_statements = []
        self.outer_post_statements = []
        self.outer_pre = []
        self.outer_post = []
        self.label = None
        self.atomic = False
        self.flag = False # just for loop permutation
        ## Hack
        self.flag_not_in_mesh = None

    def update_label(self, label):
        self.label = label

    def update_atomicity(self, boolean):
        self.atomic = boolean

    def debug_print(self):
        string = ""

        # for stmt in self.outer_pre_statements:
        #     string += stmt.debug_print()
        #string += self.iterator.debug_print() + "\n" \
            #                  + "Body: " 
     
        if self.iterator != None:
            print self.iterator.debug_print() + "\n" \
                + "Body: " 

        if self.body != None:
            for bod in self.body:
                print bod.debug_print()
            # for bod in self.body:
            #     string += bod.debug_print()
        if self.outer_post_statements != None:
            for stmt in self.outer_post_statements:
                print stmt.debug_print()
        #return string
    

    """
    def prettyprint_C_loop(self, depth, iters, indent):
        
        string = indent        
        parallinfo = ""
        iterator = "i" + depth
        if iterator not in iters:
            iters.append(iterator)

        ## redef temporaire
        iterator = self.iterator[0].name

        if self.iterator[0].kind == "piter":
            if self.iterator[0].parallelism == "THRD":
                parallinfo += "#pragma omp parallel for " 
                if self.iterator[0].private_variables != None:
                    parallinfo += "private("
                    for pri in self.iterator[0].private_variables[1:]:
                        parallinfo += pri + ","
                    parallinfo += self.iterator[0].private_variables[len(self.iterator[0].private_variables)-1]
                    parallinfo += ") "

                if self.iterator[0].schedule != None:
                    parallinfo += "schedule(static, " + self.iterator[0].schedule + ")\n"

            if self.iterator[0].parallelism == "VEC":
                ### Test
                parallinfo += "#pragma omp for simd\n" + indent

            
        ### In case there is peeling before loop
        for stmt in self.outer_pre_statements:
            string += stmt.prettyprint_C_statement(indent)
        
        string += parallinfo
 
        string += "for(" + iterator + " = " + self.iterator[0].minbound + "; " 
        
        if self.iterator[0].reversed == True:
            string += iterator + " > " + self.iterator[0].maxbound + "; "
            string += iterator + " -= " + self.iterator[0].stride 
        else:
            string += iterator + " < " + self.iterator[0].maxbound + "; "
            string += iterator + " += " + self.iterator[0].stride

        string += ") {\n"
        
        for stmt in self.outer_post_statements:
            string += stmt.prettyprint_C_statement(indent)
        indent += " "
        
        for bod in self.body:
            if bod.__class__.__name__ == "Loop":
                string += bod.prettyprint_C_loop(str(int(depth) + 1), iters, indent)
            else:
                
                string += bod.prettyprint_C_statement(indent)
        
        string += indent + "}\n"

        return string
    """ 
