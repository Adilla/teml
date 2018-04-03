from copy import deepcopy, copy
from termcolor import colored
import sys


class IvieDependency():
    def __init__(self, type_, source, sink, condition):
        self.type = type_
        self.source = source
        self.sink = sink
        self.condition = condition
        self.garbage = False

    def debug_print(self):
        string = colored("Dependency: ", "yellow", attrs=["bold"]) \
                 + colored(self.type, attrs=["bold"]) + "{ Sink: " \
                 + self.sink.debug_print() + ", Source: " \
                 + self.source.debug_print() + ", Condition: " 

        if self.condition != None:
            string += self.condition 
        else:
            string += "None"            
        string += "\n"

        return string

    def mark_as_garbage(self):
        self.garbage = True


class IvieArgument():
    """ Type
    array: IvieArray
    indexes: list of IvieIterator
    dump: string
    """

    def __init__(self, array, indexes, dump):
        self.array = array
        self.indexes = indexes
        self.indexes_dump = None
        self.string = dump


    def debug_print(self):
        string = colored(self.array.name, "red", attrs=["bold"])
        for index in self.indexes:
            string += "[" + colored(index.name, "blue", attrs=["bold"]) + "]"
        string += " "
        return string
    
    ### for CFD: manipulating one-dimensional arrays
    ### We store the different iterators normally
    ### but at code generation, must consider 
    ### restoring original access function such as 
    ### v[(i6 + 3*(i5 + 2 *(i4)))]
    def set_indexes_dump(self, dump):
        self.indexes_dump = dump
        
    def prettyprint_C_argument(self):
        string = self.array.name
        for index in self.indexes:
            string += "[" + index.name + "]"
       
        return string


class IvieStatement():
    """ Type
    name: String
    store: IvieArgument
    args: IvieArgument
    """

    def __init__(self, name, store, args):
        self.name = name
        self.store = store
        self.args = args
        self.label = None
        self.atomic = False

    def update_label(self, label):
        self.label = label

    def update_atomicity(self, boolean):
        self.atomic = boolean

    def debug_print(self):
        string = "\n--" + self.name + "--" + "\nStore: " \
                 + self.store.debug_print() 
        string += " - Args: "
        for arg in self.args:
            string += arg.debug_print()
        return string

    """
    def prettyprint_C_statement(self, indent):
        string = ""
        if self.atomic == True:
            string += "#pragma omp atomic\n"
        string += indent + self.store.prettyprint_C_argument()

        if self.args != []:
            string += " = " + self.args[0].prettyprint_C_argument()
            for arg in self.args[1:]:
                string += ", " + arg.prettyprint_C_argument()
            
        string += ";\n"
        return string
    """

class IvieLoop():
    """ Types
    iterators: list of IvieIterators
    body: list of either IvieStatement or IvieLoop
    """
  
    def __init__(self, iterators, body):
        self.iterators = iterators
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

        for stmt in self.outer_pre_statements:
            string += stmt.debug_print()
        string += self.iterators.debug_print() + "\n" \
                  + "Body: " 
        
        for bod in self.body:
            string += bod.debug_print()
            
        for stmt in self.outer_post_statements:
            string += stmt.debug_print()
        return string


    """
    def prettyprint_C_loop(self, depth, iters, indent):
        
        string = indent        
        parallinfo = ""
        iterator = "i" + depth
        if iterator not in iters:
            iters.append(iterator)

        ## redef temporaire
        iterator = self.iterators[0].name

        if self.iterators[0].kind == "piter":
            if self.iterators[0].parallelism == "THRD":
                parallinfo += "#pragma omp parallel for " 
                if self.iterators[0].private_variables != None:
                    parallinfo += "private("
                    for pri in self.iterators[0].private_variables[1:]:
                        parallinfo += pri + ","
                    parallinfo += self.iterators[0].private_variables[len(self.iterators[0].private_variables)-1]
                    parallinfo += ") "

                if self.iterators[0].schedule != None:
                    parallinfo += "schedule(static, " + self.iterators[0].schedule + ")\n"

            if self.iterators[0].parallelism == "VEC":
                ### Test
                parallinfo += "#pragma omp for simd\n" + indent

            
        ### In case there is peeling before loop
        for stmt in self.outer_pre_statements:
            string += stmt.prettyprint_C_statement(indent)
        
        string += parallinfo
 
        string += "for(" + iterator + " = " + self.iterators[0].minbound + "; " 
        
        if self.iterators[0].reversed == True:
            string += iterator + " > " + self.iterators[0].maxbound + "; "
            string += iterator + " -= " + self.iterators[0].stride 
        else:
            string += iterator + " < " + self.iterators[0].maxbound + "; "
            string += iterator + " += " + self.iterators[0].stride

        string += ") {\n"
        
        for stmt in self.outer_post_statements:
            string += stmt.prettyprint_C_statement(indent)
        indent += " "
        
        for bod in self.body:
            if bod.__class__.__name__ == "IvieLoop":
                string += bod.prettyprint_C_loop(str(int(depth) + 1), iters, indent)
            else:
                
                string += bod.prettyprint_C_statement(indent)
        
        string += indent + "}\n"

        return string
    """ 
