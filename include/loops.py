from copy import deepcopy, copy
from termcolor import colored
import sys


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

        print self.iterator.debug_print() + "\n" \
                  + "Body: " 

        for bod in self.body:
            print bod.debug_print()
        # for bod in self.body:
        #     string += bod.debug_print()
            
        # for stmt in self.outer_post_statements:
        #     string += stmt.debug_print()
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
