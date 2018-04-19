from copy import deepcopy, copy
from termcolor import colored
from utils import *
import subprocess

class Subscript():
    tensor = None
    access = None

    def __init__(self, tensor, access):
        self.tensor = tensor
        self.access = access

    def debug_print(self):
        string = self.tensor.name + "["
        if self.access != []:
            string += str(self.access[0])
        
            for data in self.access[1:]:
                string += ', ' + str(data)
        string += ']'
        return string

class Expression():
    op = None
    left = None
    right = None
    store = None
    ranks = None

    
    def __init__(self, op, left, right, store):
        self.op = op
        self.left = left
        self.right = right
        self.store = store

    def update_store(self, store):
        self.store = store

    def update_ranks(self, ranks):
        self.ranks = ranks
        
    def debug_print(self):
        # debugleft = None
        # debugright = None
        # if self.left != None:
        #     debugleft = self.left.debug_print()
        # if self.right != None:
        #     debugright = self.right.debug_print()
        # return "(" + self.op + ", " + debugleft + ", " + debugright + ")"
        tleft = None
        tright = None
        tstore = None
        if self.left != None:
            tleft = self.left.debug_print()
        if self.right != None:
            tright = self.right.debug_print()
        if self.store != None:
            tstore = self.store.debug_print()
        return (tstore, self.op, tleft, tright)

class Tensor():
    dtype = None
    shape = None
    expr = None
    parent = None
    construct = None
    debug_str = None
    

    def __init__(self, name, dtype, shape, expr, parent, construct):
        self.name = name
        self.dtype = dtype
        self.shape = shape
        self.expr = expr
        self.parent = parent
        self.construct = construct
    
        """
        if self.expr != None:
            print (self.dtype, self.name, self.shape, self.expr.debug_print(),\
                   self.parent, self.construct)
        """
            
    def debug_print(self):
        if self.expr != None:
            print (self.dtype, self.name, self.shape, self.expr.debug_print(),\
                   self.parent, self.construct)


    def infer_range(self):
        ## Infer range of output tensor.
       

        if self.expr != None:
            # Collect constraints
            # in string format for ISCC
            constraints = []
            indexes = []

            
            constraints = collect_constraints(constraints, indexes, self.expr)

            indexes = ", ".join(indexes)
            indexes = "S[" + indexes + "]"
            constraints = " and ".join(constraints)
            constraints = "D := { " + indexes + ": " + constraints + " };\n"
            outsub = ", ".join(self.expr.store.access)
            write = self.name + "[" + outsub + "]"
            # Build relation with output tensor
            relation = "W := { " + indexes + " -> " + write + "} * D;\n"
            irange = "R := ran W;\n"
            lexmax = "L := lexmax R;\n"
            result = "print L;\n"
            iscc_script = constraints + relation + irange + lexmax + result

            with open("_script.iscc", "w") as source:
                source.write(iscc_script)

            # I don't know why the following does not work
            #rrange = subprocess.call(['~/Tools/barvinok-0.41/iscc', '<', '_script.iscc'])
            # I will generate a sh file containing the command
            with open("_bscript.sh", "w") as source:
                command = "~/Tools/barvinok-0.41/iscc < _script.iscc"
                source.write(command)

            rrange = subprocess.check_output(["zsh", "_bscript.sh"])

            rrange = rrange.replace(self.name, "").\
                     replace("{ ", "").\
                     replace(" }", "").\
                     replace("\n", "")
            self.shape = rrange

            print self.debug_print()
             
    def build(self, iterators):
        ## This is the old implementation
        ## (for imperative transformations)
        for data in self.expr.ranks:
            print ("i" + data, 0, self.expr.ranks[data], 1)
        
    

        
